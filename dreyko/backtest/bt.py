"""Dreyko ilk tur backtest (kullanıcı kararıyla sapma; kurallar karar_gunlugu.md "Backtest").

Yalnızca IS 2020-2025. Olay tanımları adim0/events.py ile aynı. SL-first.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "adim0"))
sys.path.insert(0, str(HERE.parent / "faz0"))

import events as E  # noqa: E402

TICK = 0.25
COST_PTS = {"NQ": 0.70, "ES": 0.33}     # $4 RT + kayma (NQ 1 tick/taraf, ES 0.5 tick/taraf), ham puan
POINT_VALUE = {"NQ": 20.0, "ES": 50.0}


def simulate(day: E.Day, start: int, entry: float, d: int, stop: float, tgt: float, limit_bar: bool):
    """Çıkış fiyatı ve nedeni. start = giriş barı. limit_bar: giriş barında yalnız stop kontrolü."""
    noon = day.base + E.NOON
    for k in range(start, len(day.tm)):
        if day.tm[k] >= noon:
            return float(day.o[k]), "time"
        o, h, l = day.o[k], day.h[k], day.l[k]
        if k == start and limit_bar:
            if (l <= stop) if d > 0 else (h >= stop):
                return float(stop), "stop"
            continue
        if k > start:                                   # boşluklu açılış
            if (o <= stop) if d > 0 else (o >= stop):
                return float(o), "stop_gap"
            if (o >= tgt) if d > 0 else (o <= tgt):
                return float(tgt), "target_gap"
        if (l <= stop) if d > 0 else (h >= stop):       # SL-first
            return float(stop), "stop"
        if (h >= tgt) if d > 0 else (l <= tgt):
            return float(tgt), "target"
    return float(day.c[-1]), "eod"


def h1_entry(day: E.Day, ev: E.Event, adj: float, through_ticks: int):
    """FPFVG yakın kenarına limit; dolum için kenarı through_ticks tick geçmeli."""
    r = ev.refs
    d = ev.d
    edge = r["fvg_hi"] if d > 0 else r["fvg_lo"]
    thr = through_ticks * TICK * adj
    for j in range(r["fvg_i"] + 1, len(day.tm)):
        if day.mod[j] > r["retest_end"]:
            return None
        hit = day.l[j] <= edge - thr if d > 0 else day.h[j] >= edge + thr
        if hit:
            fill = min(day.o[j], edge) if d > 0 else max(day.o[j], edge)
            return j, float(fill)
    return None


def make_trade(sym, day, other, ev, adj, target, through_ticks=1):
    """ev: FPFVG_form (H1), IFVG (H2) ya da TSCISD (H2b). None = işlem yok."""
    tick = TICK * adj
    d = ev.d
    pm = ev.refs.get("pm")
    if ev.event == "FPFVG_form":
        got = h1_entry(day, ev, adj, through_ticks)
        if got is None:
            return None
        j, entry = got
        stop = ev.refs["leg_ext"] - d * tick
        limit_bar = True
        pm_o = E.pm_range(other) if other is not None else None
        smt = E.smt_support(day, other, pm, pm_o, int(day.tm[j]), d)
    else:
        j, entry = ev.entry_idx, ev.entry_px
        stop = ev.refs["ext"] - d * tick
        limit_bar = False
        smt = ev.feats["smt"]
    risk = (entry - stop) * d
    if not risk > 0:
        return None
    if target == "L":
        if pm is None:
            return None
        tgt = pm[0] if d > 0 else pm[1]
        if not (tgt - entry) * d > 0:
            return None
    else:
        tgt = entry + d * 2 * risk
    tdist = (tgt - entry) * d
    exit_px, why = simulate(day, j, entry, d, stop, tgt, limit_bar)
    cost = COST_PTS[sym] * adj
    gross = (exit_px - entry) * d
    # permütasyon için: aynı giriş, aynı mesafeler, ters yön
    x2, _ = simulate(day, j, entry, -d, entry + d * risk, entry - d * tdist, limit_bar)
    gross_flip = (x2 - entry) * (-d)
    em = int(day.mod[j])
    return {"sym": sym, "date": day.date, "year": day.date.year, "d": d, "entry_mod": em,
            "entry": entry, "stop": stop, "tgt": tgt, "exit": exit_px, "why": why,
            "risk_pts": risk / adj, "gross_pts": gross / adj, "net_pts": (gross - cost) / adj,
            "R": (gross - cost) / risk, "R_flip": (gross_flip - cost) / risk,
            "usd": (gross - cost) / adj * POINT_VALUE[sym],
            "smt": smt, "makro": E.MACRO[0] <= em <= E.MACRO[1]}


def metrics(t: pd.DataFrame, n_perm=10_000, seed=0) -> dict:
    if len(t) == 0:
        return {"n": 0}
    R = t.R.to_numpy()
    top2 = np.sort(R)[-2:].sum() if len(R) >= 2 else R.sum()
    pos, neg = R[R > 0].sum(), -R[R < 0].sum()
    eq = t.sort_values("date").usd.cumsum().to_numpy()
    dd = (np.maximum.accumulate(np.r_[0, eq]) - np.r_[0, eq]).max()
    yr = t.groupby("year").R.sum()
    rng = np.random.default_rng(seed)
    flip = rng.random((n_perm, len(t))) < 0.5
    sims = np.where(flip, t.R_flip.to_numpy(), R).sum(axis=1)
    p = (1 + (sims >= R.sum()).sum()) / (n_perm + 1)
    return {
        "n": len(t), "win": (R > 0).mean(), "avgR": R.mean(), "medR": np.median(R),
        "totR": R.sum(), "noTop2R": R.sum() - top2, "PF": pos / neg if neg > 0 else np.inf,
        "usd": t.usd.sum(), "maxDD_usd": dd, "yrs_pos": f"{(yr > 0).sum()}/{len(yr)}",
        "longR": t[t.d == 1].R.mean(), "shortR": t[t.d == -1].R.mean(),
        "be_cost_pts": t.gross_pts.mean(), "avg_risk_pts": t.risk_pts.mean(),
        "stop%": t.why.str.startswith("stop").mean(), "tgt%": t.why.str.startswith("target").mean(),
        "time%": (t.why == "time").mean(), "perm_p": p,
    }
