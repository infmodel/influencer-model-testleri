"""Seçicilik turu filtreleri (ön kayıt: karar_gunlugu.md "Seçicilik turu").

Bilgi kesimi: giriş barının açılışından ÖNCE açılmış (ve dolayısıyla kapanmış) barlar.
Market girişte karar barı kapanışı = giriş barı açılışı; limit girişte dolum barından öncekiler.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

NS = 60_000_000_000
ASIA_START = -240        # gün başına göre dakika: önceki akşam 20:00
SESSION_START = -360     # 18:00
RTH_OPEN = 570


def session_bars(df: pd.DataFrame) -> dict:
    """session_date → (tm, h, l) tüm seans barları (18:00 → 17:00)."""
    tm = df.index.asi8 // NS
    sd = df["session_date"].to_numpy()
    h, l = df["high"].to_numpy(float), df["low"].to_numpy(float)
    out = {}
    cuts = np.flatnonzero(sd[1:] != sd[:-1]) + 1
    starts = np.r_[0, cuts]
    ends = np.r_[cuts, len(sd)]
    for a, b in zip(starts, ends):
        out[pd.Timestamp(sd[a])] = (tm[a:b], h[a:b], l[a:b])
    return out


def day_base(date: pd.Timestamp) -> int:
    return int(pd.Timestamp(date).value // NS)


def levels(sb: dict, atr: pd.Series) -> pd.DataFrame:
    rows = {}
    prev = None
    for d in sorted(sb):
        tm, h, l = sb[d]
        base = day_base(d)
        m = (tm >= base + ASIA_START) & (tm < base)
        r = {"asia_hi": h[m].max() if m.any() else np.nan,
             "asia_lo": l[m].min() if m.any() else np.nan,
             "pd_hi": prev[1].max() if prev is not None else np.nan,
             "pd_lo": prev[2].min() if prev is not None else np.nan}
        rows[d] = r
        prev = (tm, h, l)
    lv = pd.DataFrame.from_dict(rows, orient="index")
    ratio = (lv.asia_hi - lv.asia_lo) / atr.reindex(lv.index)
    lv["asia_ratio"] = ratio
    # nedensel eşik: önceki günlerin genişleyen medyanı (bugün dahil değil)
    lv["asia_med"] = ratio.expanding(min_periods=60).median().shift(1)
    return lv


def _ext(tm, x, a, b, fn, empty):
    m = (tm >= a) & (tm < b)
    return fn(x[m]) if m.any() else empty


def flags(date, entry_mod: int, d: int, sb: dict, lv_row) -> dict:
    tm, h, l = sb[date]
    base = day_base(date)
    entry, t930, s0 = base + entry_mod, base + RTH_OPEN, base + SESSION_START
    hmax = lambda a, b: _ext(tm, h, a, b, np.max, -np.inf)
    lmin = lambda a, b: _ext(tm, l, a, b, np.min, np.inf)
    if d > 0:
        opp = [(lv_row["asia_lo"], base), (lv_row["pd_lo"], s0)]
        own = [(lv_row["asia_hi"], base), (lv_row["pd_hi"], s0)]
        f1 = any(np.isfinite(L) and lmin(st, t930) >= L and lmin(t930, entry) < L for L, st in opp)
        f2 = any(np.isfinite(H) and hmax(st, entry) <= H for H, st in own)
    else:
        opp = [(lv_row["asia_hi"], base), (lv_row["pd_hi"], s0)]
        own = [(lv_row["asia_lo"], base), (lv_row["pd_lo"], s0)]
        f1 = any(np.isfinite(H) and hmax(st, t930) <= H and hmax(t930, entry) > H for H, st in opp)
        f2 = any(np.isfinite(L) and lmin(st, entry) >= L for L, st in own)
    r, med = lv_row["asia_ratio"], lv_row["asia_med"]
    f3 = bool(np.isfinite(r) and np.isfinite(med) and r < med)
    return {"F1": bool(f1), "F2": bool(f2), "F3": f3}
