"""MA: günlük bias isabeti (I-MA2) ve MA-T işlem katmanı. Ön kayıt §1."""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C


def ma_days(inst: C.Inst, boundary: str) -> pd.DataFrame:
    """Her uygun D için (D-1, D, D+1 geçerli) durum, bias ve D+1 etiketleri. Satır = D+1 (işlem günü)."""
    d = C.days(inst, boundary)
    st = C.state_series(d).to_numpy()
    H, L, Cl = d["high"].to_numpy(), d["low"].to_numpy(), d["close"].to_numpy()
    ok = d["ok"].to_numpy()
    atr = d["atr"].to_numpy()
    i0s, i1s = d["i0"].to_numpy(), d["i1"].to_numpy()
    rows = []
    for k in range(1, len(d) - 1):
        if not (ok[k - 1] and ok[k] and ok[k + 1]) or not np.isfinite(atr[k + 1]):
            continue
        s = st[k]
        a, b = i0s[k + 1], i1s[k + 1]
        hh, ll = inst.h[a:b + 1], inst.l[a:b + 1]
        upH, dnL = C.first_true(hh >= H[k]), C.first_true(ll <= L[k])
        # post-hoc ayna kontrolü: C_D'den hedefe olan mesafe kadar karşı yönde seviye
        bias_k = C.BIAS.get(st[k], 0)
        mir = np.nan
        if bias_k != 0:
            dist = abs((H[k] if bias_k == 1 else L[k]) - Cl[k])
            lvl = Cl[k] - bias_k * dist
            mir = float(L[k + 1] <= lvl) if bias_k == 1 else float(H[k + 1] >= lvl)
        rec = {"date": d.index[k + 1], "state": s, "bias": C.BIAS.get(s, 0),
               "hitH": float(H[k + 1] >= H[k]), "hitL": float(L[k + 1] <= L[k]),
               # hangisi önce: aynı dakikada ikisi -> karşı uç önce (muhafazakâr), aşağıda yöne göre
               "firstH": upH, "firstL": dnL,
               "ret_cc": (Cl[k + 1] - Cl[k]) / atr[k + 1], "atr": atr[k + 1], "hit_mirror": mir,
               "tgt_dist_atr": (abs((H[k] if bias_k == 1 else L[k]) - Cl[k]) / atr[k + 1]) if bias_k else np.nan}
        rows.append(rec)
    df = pd.DataFrame(rows)
    df["year"] = df["date"].dt.year
    b = df["bias"].to_numpy()
    fH, fL = df["firstH"].to_numpy(), df["firstL"].to_numpy()
    big = 10**9
    fH2, fL2 = np.where(fH < 0, big, fH), np.where(fL < 0, big, fL)
    # long bias: hedef H önce (kesin önce) -> 1; short: L kesin önce -> 1; hiçbiri -> 0
    first_bias = np.where(b == 1, (fH2 < fL2), np.where(b == -1, (fL2 < fH2), np.nan)).astype(float)
    none = (fH < 0) & (fL < 0)
    first_bias[none & (b != 0)] = 0.0
    df["first_bias"] = first_bias
    df["hit_bias"] = np.where(b == 1, df.hitH, np.where(b == -1, df.hitL, np.nan))
    df["hit_opp"] = np.where(b == 1, df.hitL, np.where(b == -1, df.hitH, np.nan))
    df["dret_cc"] = b * df["ret_cc"]
    return df


def ma_t_events(inst: C.Inst, boundary: str) -> list[dict]:
    """MA-T: D+1'de 09:00 TR sonrası %50 ucuz/pahalı geçişi + 1S konfirme; market; stop 09:00'dan beri uç;
    TP günlük hedef; RR >= 1.8; konfirme kapanışı <= 19:00 TR."""
    d = C.days(inst, boundary)
    md_ = ma_days(inst, boundary)
    h1 = C.bars(inst, 60)
    h1t = pd.DatetimeIndex(h1.index).asi8
    dom = C.day_of_minute(inst, boundary)
    H, L = d["high"].to_numpy(), d["low"].to_numpy()
    pos = {dt: k for k, dt in enumerate(d.index)}
    evs = []
    for r in md_[md_.bias != 0].itertuples():
        k1 = pos[r.date]
        k = k1 - 1
        bias = r.bias
        tgt = H[k] if bias == 1 else L[k]
        mid = 0.5 * (H[k] + L[k])
        day_start = np.int64(pd.Timestamp(r.date).value) - C.TR_OFF  # TR 00:00 = UTC 21:00 önceki gün
        t09 = day_start + 9 * 60 * C.MIN
        t18 = day_start + 18 * 60 * C.MIN   # son konfirme mumunun açılışı 18:00 TR (kapanış 19:00)
        j0, j1 = np.searchsorted(h1t, t09), np.searchsorted(h1t, t18, side="right")
        if j1 <= j0:
            continue
        seg = h1.iloc[j0:j1]
        # 1S mumlar D+1 gününe ait olmalı
        if (dom[seg["i0"].to_numpy()] != k1).any():
            seg = seg[dom[seg["i0"].to_numpy()] == k1]
            if seg.empty:
                continue
        hh, ll, cc = seg["high"].to_numpy(), seg["low"].to_numpy(), seg["close"].to_numpy()
        cheap = False
        ext_i = -1
        ext = np.inf if bias == 1 else -np.inf
        for j in range(len(seg)):
            if (bias == 1 and hh[j] >= tgt) or (bias == -1 and ll[j] <= tgt):
                break                       # hedef konfirmeden önce alındı -> gün iptal
            if bias == 1:
                if ll[j] < mid:
                    cheap = True
                if ll[j] < ext:
                    ext, ext_i = ll[j], j
                    continue                # yeni uç yapan mum konfirme olamaz
                conf = cheap and ext_i >= 0 and cc[j] > hh[ext_i]
            else:
                if hh[j] > mid:
                    cheap = True
                if hh[j] > ext:
                    ext, ext_i = hh[j], j
                    continue
                conf = cheap and ext_i >= 0 and cc[j] < ll[ext_i]
            if conf:
                i0 = C.next_idx(inst, pd.Timestamp(seg["t_last"].iat[j]).value)
                if i0 >= len(inst.t) or dom[i0] != k1:
                    break
                entry = inst.o[i0]
                risk = bias * (entry - ext)
                rr = bias * (tgt - entry) / risk if risk > 0 else -1
                if risk > 0 and rr >= 1.8:
                    evs.append({"model": "MA-T", "date": r.date, "d": bias, "i0": i0, "entry": entry,
                                "stop": ext, "tp": tgt, "iend": int(d["i1"].iat[k1]), "fill_partial": False,
                                "state": r.state})
                break
    return evs
