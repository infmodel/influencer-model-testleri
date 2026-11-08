"""MB: 15dk marubozu açılışına limit, 1R (Sk5). Ön kayıt §4."""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C

PIV_L = 5
WAIT_BARS = 10
MAX_STOP_PIP = 20.0
BUF_PIP = 1.5
TR_LO, TR_HI = 8 * 60, 18 * 60     # TR dakikası


def wma(x: np.ndarray, n: int) -> np.ndarray:
    w = np.arange(1, n + 1, dtype=float)
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        from numpy.lib.stride_tricks import sliding_window_view as sw
        out[n - 1:] = sw(x, n) @ w / w.sum()
    return out


def mb_features(inst: C.Inst) -> pd.DataFrame:
    """15dk barlarda nedensel trend/yapı durumu (bar kapanışında bilinen)."""
    b = C.bars(inst, 15).copy()
    h, l, c, o = (b[k].to_numpy() for k in ("high", "low", "close", "open"))
    n = len(b)
    b["sma21"] = pd.Series(c).rolling(21).mean().to_numpy()
    b["swma"] = pd.Series(wma(c, 26)).rolling(5).mean().to_numpy()
    ph, pl = C.pivots(h, l, PIV_L)
    struct = np.zeros(n, int)       # bar k kapanışından sonra yapı: 1 bullish, -1 bearish
    last_ph = np.full(n, np.nan)    # bar k kapanışında bilinen son onaylı pivot high/low
    last_pl = np.full(n, np.nan)
    last_pl_i = np.full(n, -1)
    cur_ph = cur_pl = np.nan
    cur_pl_i = -1
    ph_broken = pl_broken = True
    s = 0
    for k in range(n):
        j = k - PIV_L                # bar k kapanınca j pivotu onaylanır
        if j >= 0 and ph[j]:
            cur_ph, ph_broken = h[j], False
        if j >= 0 and pl[j]:
            cur_pl, cur_pl_i, pl_broken = l[j], j, False
        if not ph_broken and c[k] > cur_ph:
            s, ph_broken = 1, True
        if not pl_broken and c[k] < cur_pl:
            s, pl_broken = -1, True
        struct[k] = s
        last_ph[k], last_pl[k], last_pl_i[k] = cur_ph, cur_pl, cur_pl_i
    # kısa için son onaylı pivot high'ın indeksi
    last_ph_i = np.full(n, -1)
    cur = -1
    for k in range(n):
        j = k - PIV_L
        if j >= 0 and ph[j]:
            cur = j
        last_ph_i[k] = cur
    b["struct"], b["last_ph"], b["last_pl"] = struct, last_ph, last_pl
    b["last_ph_i"], b["last_pl_i"] = last_ph_i, last_pl_i
    b["bull_m"] = (c > o) & (o == l)
    b["bear_m"] = (c < o) & (o == h)
    # itki bacağı: high, son onaylı pivot low'dan beri en yüksek (long); short simetrik
    imp_l = np.zeros(n, bool)
    imp_s = np.zeros(n, bool)
    for k in range(n):
        a = last_pl_i[k]
        if a >= 0:
            imp_l[k] = h[k] >= h[a:k + 1].max()
        a = last_ph_i[k]
        if a >= 0:
            imp_s[k] = l[k] <= l[a:k + 1].min()
    b["imp_l"], b["imp_s"] = imp_l, imp_s
    b["tr_close_min"] = C.tr_minute(pd.DatetimeIndex(b.index).asi8 + 15 * C.MIN)
    return b


def mb_events(inst: C.Inst, variant: str, feats: pd.DataFrame | None = None) -> list[dict]:
    """variant: 'v' (SMA21), 's' (WMA26->SMA5), 'h0' (filtresiz tüm marubozular)."""
    b = feats if feats is not None else mb_features(inst)
    d = C.days(inst, "ny17")
    dom = C.day_of_minute(inst, "ny17")
    ok = d["ok"].to_numpy()
    ma = b["sma21"].to_numpy() if variant == "v" else b["swma"].to_numpy()
    o, h, l, c = (b[k].to_numpy() for k in ("open", "high", "low", "close"))
    t = pd.DatetimeIndex(b.index).asi8
    tcm = b["tr_close_min"].to_numpy()
    full = b["n_min"].to_numpy() >= 14
    evs = []
    used_days = set()
    for k in np.flatnonzero((b["bull_m"] | b["bear_m"]).to_numpy() & full):
        if not (TR_LO <= tcm[k] <= TR_HI):
            continue
        dirn = 1 if b["bull_m"].iat[k] else -1
        if variant != "h0":
            if not np.isfinite(ma[k]):
                continue
            if dirn == 1 and not (c[k] > ma[k] and b["struct"].iat[k] == 1 and b["imp_l"].iat[k]):
                continue
            if dirn == -1 and not (c[k] < ma[k] and b["struct"].iat[k] == -1 and b["imp_s"].iat[k]):
                continue
        sw = b["last_pl"].iat[k] if dirn == 1 else b["last_ph"].iat[k]
        if not np.isfinite(sw):
            continue
        stop = sw - BUF_PIP * inst.pip if dirn == 1 else sw + BUF_PIP * inst.pip
        lim = o[k]
        if dirn * (lim - sw) <= 0:          # son pivot, marubozu açılışının ötesinde değilse stop anlamsız
            continue
        a = np.searchsorted(inst.t, t[k] + 15 * C.MIN)
        e = np.searchsorted(inst.t, t[k] + (15 + 15 * WAIT_BARS) * C.MIN) - 1
        if e < a:
            continue
        seg = inst.l[a:e + 1] <= lim if dirn == 1 else inst.h[a:e + 1] >= lim
        f = C.first_true(seg)
        if f < 0:
            continue
        i0 = a + f
        if not (TR_LO <= C.tr_minute(inst.t[i0:i0 + 1])[0] < TR_HI):
            continue
        kd = dom[i0]
        if kd < 0 or not ok[kd] or (kd in used_days):
            continue
        entry = min(lim, inst.o[i0]) if dirn == 1 else max(lim, inst.o[i0])
        risk = dirn * (entry - stop)
        if not (0 < risk <= MAX_STOP_PIP * inst.pip):
            continue
        used_days.add(kd)
        evs.append({"model": f"MB-{variant}", "date": d.index[kd], "d": dirn, "i0": int(i0), "entry": float(entry),
                    "stop": float(stop), "tp": float(entry + dirn * risk),
                    "iend": int(d["i1"].iat[min(kd + 5, len(d) - 1)]), "fill_partial": True,
                    "wait": int(f)})
    return evs
