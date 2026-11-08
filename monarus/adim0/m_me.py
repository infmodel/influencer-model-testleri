"""ME: 4S CRT (ME-1, ME-1n) ve haftalık bias -> günlük CRT (ME-2). Ön kayıt §2."""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C
from m_ma import ma_days

PAIRS = [(4, 8), (8, 12)]   # (1. mum, 2. mum) blok başlangıç saati (gün sınırına göre kaydırılmış yerel)


def crt_dir(H1, L1, H2, L2, C2) -> int:
    """2. mum 1. mumun bir ucunu fitille alıp içeride kapanırsa yön; iki uç birden alınmışsa 0."""
    up = H2 > H1 and L1 <= C2 <= H1      # high alındı -> short CRT
    dn = L2 < L1 and L1 <= C2 <= H1      # low alındı -> long CRT
    if up and not dn:
        return -1
    if dn and not up:
        return 1
    return 0


def me1_events(inst: C.Inst, boundary: str, filtered: bool = True) -> list[dict]:
    d = C.days(inst, boundary)
    b4 = C.h4(inst, boundary)
    md_ = ma_days(inst, boundary).set_index("date")
    pos = {dt: k for k, dt in enumerate(d.index)}
    H, L = d["high"].to_numpy(), d["low"].to_numpy()
    b4_day = pd.DatetimeIndex(b4.index).normalize()
    b4_hour = pd.DatetimeIndex(b4.index).hour
    b4 = b4.assign(day=b4_day, hour=b4_hour)
    grp = {k: g.set_index("hour") for k, g in b4.groupby("day")}
    evs = []
    for date, r in md_.iterrows():
        if filtered and r.bias == 0:
            continue
        g = grp.get(date)
        if g is None:
            continue
        k1 = pos[date]
        k = k1 - 1
        for h1, h2 in PAIRS:
            if h1 not in g.index or h2 not in g.index:
                continue
            a, b = g.loc[h1], g.loc[h2]
            if a.n_min < 192 or b.n_min < 192:        # %80 dolu blok
                continue
            dirn = crt_dir(a.high, a.low, b.high, b.low, b.close)
            if dirn == 0 or (filtered and dirn != r.bias):
                continue
            tgt = H[k] if dirn == 1 else L[k]
            i0 = C.next_idx(inst, pd.Timestamp(b.t_last).value)
            if i0 >= len(inst.t) or C.day_of_minute(inst, boundary)[i0] != k1:
                continue
            entry = inst.o[i0]
            stop = b.low if dirn == 1 else b.high
            if dirn * (tgt - entry) <= 0 or dirn * (entry - stop) <= 0:
                continue
            evs.append({"model": "ME-1" if filtered else "ME-1n", "date": date, "d": dirn, "i0": i0,
                        "entry": entry, "stop": stop, "tp": tgt, "iend": int(d["i1"].iat[k1]),
                        "fill_partial": False, "pair": f"{h1:02d}-{h2:02d}", "state": r.state})
            break
    return evs


def me2_events(inst: C.Inst, boundary: str) -> list[dict]:
    d = C.days(inst, boundary)
    w = C.weeks(inst, boundary)
    wst = C.state_series(w).to_numpy()
    wok = w["ok"].to_numpy()
    H, L, Cl = d["high"].to_numpy(), d["low"].to_numpy(), d["close"].to_numpy()
    ok = d["ok"].to_numpy()
    evs = []
    for j in range(1, len(w) - 1):
        if not (wok[j - 1] and wok[j] and wok[j + 1]):
            continue
        bias = C.BIAS.get(wst[j], 0)
        if bias == 0:
            continue
        tgt = w["high"].iat[j] if bias == 1 else w["low"].iat[j]
        ka, kb = int(w["k_first"].iat[j + 1]), int(w["k_last"].iat[j + 1])
        for k in range(ka, kb):                 # k+1 de W+1 içinde olmalı
            if k - 1 < 0 or not (ok[k - 1] and ok[k] and ok[k + 1]):
                continue
            dirn = crt_dir(H[k - 1], L[k - 1], H[k], L[k], Cl[k])
            if dirn != bias:
                continue
            i0 = int(d["i0"].iat[k + 1])
            entry = inst.o[i0]
            stop = L[k] if bias == 1 else H[k]
            if bias * (tgt - entry) <= 0 or bias * (entry - stop) <= 0:
                continue
            evs.append({"model": "ME-2", "date": d.index[k + 1], "d": bias, "i0": i0, "entry": entry,
                        "stop": stop, "tp": tgt, "iend": int(d["i1"].iat[kb]), "fill_partial": False,
                        "state": wst[j]})
            break
    return evs
