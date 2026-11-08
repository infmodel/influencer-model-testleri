"""MC: NQ 15dk açılış sonrası sweep (A: CISD gövde kapanışı, B: engulf + limit). Ön kayıt §6."""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import common as C

RTH_OPEN, LAST_CLOSE, CAP = 9 * 60 + 30, 13 * 60, 16 * 60     # NY dakikası
FRI_CUT = 12 * 60
TP_R = 1.5
NQ_TICK = 0.25
NQ_COST = 0.7       # puan, gidiş-dönüş ($4 + 2 tick)


def load_nq() -> C.Inst:
    root = C.HERE.parents[1]
    sys.path.insert(0, str(next((root / d / "faz0" for d in ("Dreyko", "dreyko") if (root / d / "faz0").exists()),
                                root / "Dreyko/faz0")))
    from dreyko_data import load_is
    df = load_is("NQ", ["open", "high", "low", "close", "ts_utc"])
    df = df.set_index(pd.DatetimeIndex(df["ts_utc"]).tz_convert("UTC") if pd.DatetimeIndex(df["ts_utc"]).tz
                      else pd.DatetimeIndex(df["ts_utc"]).tz_localize("UTC"))[["open", "high", "low", "close"]]
    df = df.sort_index()
    df = df[~df.index.duplicated()]
    C.md._guard(df.index)
    return C.make_inst("NQ", df, NQ_TICK, NQ_COST)


def rth_days(inst: C.Inst) -> dict:
    """NY tarihi -> RTH 1dk indeksleri; yalnız tam RTH (390 dk, erken kapanış yok) günleri."""
    if "rth" in inst.cache:
        return inst.cache["rth"]
    ny = pd.DatetimeIndex(inst.t).tz_localize("UTC").tz_convert(C.md.NY)
    m = ny.hour * 60 + ny.minute
    date = ny.tz_localize(None).normalize()
    sel = (m >= RTH_OPEN) & (m < CAP)
    out = {}
    idx = np.flatnonzero(sel)
    for dt, g in pd.Series(idx, index=date[idx]).groupby(level=0):
        if len(g) == 390:
            out[dt] = g.to_numpy()
    inst.cache["rth"] = out
    inst.cache["nymin"] = np.asarray(m)
    return out


def bars15(inst: C.Inst, ix: np.ndarray):
    """RTH 1dk indekslerinden 09:30 hizalı 15dk barlar (09:30..12:45 açılışlı 14 bar)."""
    o, h, l, c = inst.o[ix], inst.h[ix], inst.l[ix], inst.c[ix]
    nb = (LAST_CLOSE - RTH_OPEN) // 15
    O = o[:nb * 15:15]
    H = h[:nb * 15].reshape(nb, 15).max(1)
    L = l[:nb * 15].reshape(nb, 15).min(1)
    Cc = c[14:nb * 15:15]
    return O, H, L, Cc


def _cisd_level(O, Cc, k, dirn):
    j = k
    bear = (lambda i: Cc[i] < O[i]) if dirn == 1 else (lambda i: Cc[i] > O[i])
    if not bear(j):
        j = k - 1
        if j < 0 or not bear(j):
            return O[k]
    while j - 1 >= 0 and bear(j - 1):
        j -= 1
    return O[j]


def mc_day(inst: C.Inst, ix: np.ndarray, variant: str, fri: bool) -> dict | None:
    O, H, L, Cc = bars15(inst, ix)
    nb = len(O)
    best = None
    for dirn in (1, -1):
        ev = _scan_a(inst, ix, O, H, L, Cc, dirn, fri) if variant == "A" else _scan_b(inst, ix, O, H, L, Cc, dirn, fri)
        if ev is not None and (best is None or ev["i0"] < best["i0"]):
            best = ev
    return best


def _ok_time(k_close_min, fri):
    return k_close_min <= LAST_CLOSE and (not fri or k_close_min <= FRI_CUT)


def _scan_a(inst, ix, O, H, L, Cc, dirn, fri):
    nb = len(O)
    sw = None   # [ext, level, opp]
    for k in range(2, nb):
        if sw is None:
            prior_ext = L[:k].min() if dirn == 1 else H[:k].max()
            if (dirn == 1 and L[k] < prior_ext) or (dirn == -1 and H[k] > prior_ext):
                opp = H[:k].max() if dirn == 1 else L[:k].min()
                sw = [L[k] if dirn == 1 else H[k], _cisd_level(O, Cc, k, dirn), opp]
            continue
        ext, lvl, opp = sw
        if (dirn == 1 and H[k] > opp) or (dirn == -1 and L[k] < opp):
            return None                    # karşı taraf alındı -> iptal
        if (dirn == 1 and L[k] < ext) or (dirn == -1 and H[k] > ext):
            sw = [L[k] if dirn == 1 else H[k], _cisd_level(O, Cc, k, dirn), opp]   # yeni sweep
            continue
        if (dirn == 1 and Cc[k] > lvl) or (dirn == -1 and Cc[k] < lvl):
            close_min = RTH_OPEN + 15 * (k + 1)
            if not _ok_time(close_min, fri):
                return None
            i0 = ix[15 * (k + 1)]
            return {"d": dirn, "i0": int(i0), "entry": float(inst.o[i0]), "stop": float(ext), "fill_partial": False}
    return None


def _scan_b(inst, ix, O, H, L, Cc, dirn, fri):
    nb = len(O)
    for k in range(2, nb):
        prior_ext = L[:k].min() if dirn == 1 else H[:k].max()
        swept = (dirn == 1 and L[k] < prior_ext) or (dirn == -1 and H[k] > prior_ext)
        if not swept:
            continue
        if dirn == 1:
            eng = Cc[k] > O[k] and Cc[k] > O[k - 1] and Cc[k] > Cc[k - 1] and O[k] <= Cc[k - 1]
            lim = max(O[k - 1], Cc[k - 1])
        else:
            eng = Cc[k] < O[k] and Cc[k] < O[k - 1] and Cc[k] < Cc[k - 1] and O[k] >= Cc[k - 1]
            lim = min(O[k - 1], Cc[k - 1])
        if not eng:
            continue
        stop = L[k] if dirn == 1 else H[k]
        a = 15 * (k + 1)
        e = (LAST_CLOSE - RTH_OPEN) if not fri else (FRI_CUT - RTH_OPEN)
        if e <= a:
            return None
        seg = ix[a:e]
        risk0 = dirn * (lim - stop)
        if risk0 <= 0:
            return None
        tp0 = lim + dirn * TP_R * risk0
        fill = C.first_true(inst.l[seg] <= lim) if dirn == 1 else C.first_true(inst.h[seg] >= lim)
        tpx = C.first_true(inst.h[seg] >= tp0) if dirn == 1 else C.first_true(inst.l[seg] <= tp0)
        if fill < 0 or (0 <= tpx < fill):
            return None
        i0 = seg[fill]
        px = min(lim, inst.o[i0]) if dirn == 1 else max(lim, inst.o[i0])
        return {"d": dirn, "i0": int(i0), "entry": float(px), "stop": float(stop), "fill_partial": True}
    return None


def simulate_be(inst, i0, entry, stop, tp, d, iend, fill_partial):
    """+1R'de stop girişe (BE). SL-first; BE tetiklendiği bar içinde yeni stop sayılmaz (sonraki bardan)."""
    risk = d * (entry - stop)
    hh, ll = inst.h[i0:iend + 1], inst.l[i0:iend + 1]
    be_lvl = entry + d * risk
    for k in range(len(hh)):
        slh = (ll[k] <= stop) if d == 1 else (hh[k] >= stop)
        tph = (hh[k] >= tp) if d == 1 else (ll[k] <= tp)
        if fill_partial and k == 0:
            tph = False
        if slh:
            return d * (stop - entry) / risk
        if tph:
            return d * (tp - entry) / risk
        if (d == 1 and hh[k] >= be_lvl) or (d == -1 and ll[k] <= be_lvl):
            stop = entry
    return d * (inst.c[iend] - entry) / risk


def mc_events(inst: C.Inst, variant: str, stop_pct: float) -> list[dict]:
    rth = rth_days(inst)
    evs = []
    for dt, ix in rth.items():
        ev = mc_day(inst, ix, variant, fri=(dt.dayofweek == 4))
        if ev is None:
            continue
        risk = ev["d"] * (ev["entry"] - ev["stop"])
        if not (0 < risk <= stop_pct * ev["entry"]):
            continue
        ev.update({"model": f"MC-{variant}-{stop_pct * 100:.1f}", "date": dt,
                   "tp": ev["entry"] + ev["d"] * TP_R * risk, "iend": int(ix[-1])})
        evs.append(ev)
    return evs


def h0_random(inst: C.Inst, evs: pd.DataFrame, reps: int = 500, seed: int = 0) -> np.ndarray:
    """Her olay günü için 09:30–13:00 arası rastgele dakika ve yön, olayın stop mesafesi, 1.5R, SL-first.
    Döner: tekrar başına ortalama R (dağılım)."""
    rng = np.random.default_rng(seed)
    rth = rth_days(inst)
    out = np.zeros(reps)
    for r in range(reps):
        tot = []
        for e in evs.itertuples():
            ix = rth[e.date]
            m = rng.integers(0, LAST_CLOSE - RTH_OPEN)
            dd = rng.choice([1, -1])
            i0 = ix[m]
            entry = inst.o[i0]
            stop = entry - dd * e.risk_px
            res = C.simulate(inst, i0, entry, stop, entry + dd * TP_R * e.risk_px, dd, int(ix[-1]), False)
            tot.append(res["R"])
        out[r] = np.nanmean(tot)
    return out
