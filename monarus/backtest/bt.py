"""Monarus backtest (sapma, iddia testi): sıralı işlem, 1R, SL-first, maliyet, permütasyon, Monte Carlo, DSR.
Ön kayıt: on_kayit_bt.md. Olay tanımları adim0/m_*.py ile birebir aynı. Yalnız IS 2020-2025."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "adim0"))
import common as C  # noqa: E402
import m_ma  # noqa: E402
import m_mb  # noqa: E402
import m_mc  # noqa: E402
import m_md  # noqa: E402
import m_me  # noqa: E402
import m_mf  # noqa: E402

BOUNDS = ("ny17", "tr")
# rastgele giriş penceresi: (saat sistemi, başlangıç dk, bitiş dk)
WINDOWS = {"MB": ("tr", 8 * 60, 18 * 60), "MD": ("tr", 9 * 60, 17 * 60), "MA-T": ("tr", 9 * 60, 19 * 60),
           "MC": ("ny", 9 * 60 + 30, 13 * 60)}


def detect_all(inst: C.Inst) -> list[tuple[str, list[dict]]]:
    """(gün sınırı, olay listesi). Adım 0 run_adim0.inst_jobs ile aynı tanımlar."""
    out = []
    for b in BOUNDS:
        out.append((b, m_ma.ma_t_events(inst, b)))
        out.append((b, m_me.me1_events(inst, b)))
        out.append((b, m_me.me1_events(inst, b, filtered=False)))
        out.append((b, m_me.me2_events(inst, b)))
        p15 = m_mf.Piv15(inst, 15)
        for mode in ("1", "1k", "n"):
            out.append((b, m_mf.mf_events(inst, b, mode, p15)))
        if b == "ny17":
            out.append((b, m_mf.mf_events(inst, b, "1", p15, sweep_atr=True)))
        p30 = m_mf.Piv15(inst, 30)
        for htf in ("4S", "1G"):
            for en in ("a", "b"):
                out.append((b, m_md.md_events(inst, b, htf, en, piv30=p30)))
            out.append((b, m_md.md_events(inst, b, htf, "a", rr_filter=False, piv30=p30)))
        if b == "ny17":
            for en in ("a", "b"):
                out.append((b, m_md.md_events(inst, b, None, en, piv30=p30)))
    if inst.name in C.FX6:
        f = m_mb.mb_features(inst)
        for v in ("v", "s", "h0"):
            out.append(("ny17", m_mb.mb_events(inst, v, f)))
    return out


def detect_nq(inst: C.Inst):
    return [("ny17", m_mc.mc_events(inst, v, sp)) for v in ("A", "B") for sp in (0.005, 0.01)]


def simulate_be(inst, i0, entry, stop, tp, d, iend, fill_partial):
    """+1R'de stop girişe. Döner (R, exit_i)."""
    risk = d * (entry - stop)
    be_lvl = entry + d * risk
    for k in range(i0, iend + 1):
        hh, ll, oo = inst.h[k], inst.l[k], inst.o[k]
        slh = (ll <= stop) if d == 1 else (hh >= stop)
        tph = (hh >= tp) if d == 1 else (ll <= tp)
        if fill_partial and k == i0:
            tph = False
        if slh:
            px = oo if (k > i0 and d * (oo - stop) < 0) else stop
            return d * (px - entry) / risk, k
        if tph:
            return d * (tp - entry) / risk, k
        if (d == 1 and hh >= be_lvl) or (d == -1 and ll <= be_lvl):
            stop = entry
    return d * (inst.c[iend] - entry) / risk, iend


def fill_partial_of(model: str) -> bool:
    return model.startswith(("MF", "MB")) or model.endswith("-b") or model.startswith("MC-B")


def sequential(inst: C.Inst, evs: list[dict], boundary: str, be: bool = False) -> list[dict]:
    """Tek açık pozisyon: önceki işlem kapanmadan gelen olay atlanır."""
    evs = sorted(evs, key=lambda e: e["i0"])
    last_exit = -1
    out = []
    for e in evs:
        if e["i0"] <= last_exit:
            continue
        fp = e.get("fill_partial", fill_partial_of(e["model"]))
        if be:
            R, ex = simulate_be(inst, e["i0"], e["entry"], e["stop"], e["tp"], e["d"], e["iend"], fp)
            hit = float(R >= m_mc.TP_R - 1e-9)
        else:
            r = C.simulate(inst, e["i0"], e["entry"], e["stop"], e["tp"], e["d"], e["iend"], fp)
            R, ex, hit = r["R"], r["exit_i"], r["hit"]
        risk = e["d"] * (e["entry"] - e["stop"])
        last_exit = ex
        out.append({"model": e["model"] + ("-BE" if be else ""), "inst": inst.name, "boundary": boundary,
                    "d": e["d"], "i0": e["i0"], "exit_i": ex, "iend": e["iend"], "entry": e["entry"],
                    "stop": e["stop"], "tp": e["tp"], "risk_px": risk, "rr": e["d"] * (e["tp"] - e["entry"]) / risk,
                    "R": R, "hit": hit, "cost_R": inst.cost / risk, "R_net": R - inst.cost / risk,
                    "t_entry": pd.Timestamp(inst.t[e["i0"]], tz="UTC"),
                    "t_exit": pd.Timestamp(inst.t[ex], tz="UTC"), "risk_pip": risk / inst.pip})
    return out


# ---------------------------------------------------------------------------
def _window_minutes(inst: C.Inst, model: str, k: int, boundary: str, cache: dict) -> np.ndarray:
    key = (model.split("-")[0] if not model.startswith("MA-T") else "MA-T", k, boundary)
    if key in cache:
        return cache[key]
    d = C.days(inst, boundary)
    a, b = int(d["i0"].iat[k]), int(d["i1"].iat[k])
    ix = np.arange(a, b + 1)
    w = WINDOWS.get(key[0])
    if w is not None:
        if w[0] == "tr":
            m = C.tr_minute(inst.t[ix])
        else:
            m = inst.cache["nymin"][ix] if "nymin" in inst.cache else \
                (pd.DatetimeIndex(inst.t[ix]).tz_localize("UTC").tz_convert(C.md.NY).hour * 60
                 + pd.DatetimeIndex(inst.t[ix]).tz_localize("UTC").tz_convert(C.md.NY).minute).to_numpy()
        ix = ix[(m >= w[1]) & (m < w[2])]
    cache[key] = ix
    return ix


def random_entry(inst: C.Inst, tr: pd.DataFrame, boundary: str, reps: int, seed: int) -> np.ndarray:
    """Her işlemin günü korunur; pencerede rastgele dakika ve yön; aynı risk, RR ve süre. Ort. R_net dağılımı."""
    rng = np.random.default_rng(seed)
    dom = C.day_of_minute(inst, boundary)
    cache: dict = {}
    n = len(inst.t)
    rows = list(tr.itertuples())
    pools = [_window_minutes(inst, r.model, dom[r.i0], boundary, cache) for r in rows]
    out = np.empty(reps)
    for rep in range(reps):
        acc = []
        for r, pool in zip(rows, pools):
            if len(pool) == 0:
                continue
            i0 = int(pool[rng.integers(len(pool))])
            dd = 1 if rng.random() < 0.5 else -1
            entry = inst.o[i0]
            stop = entry - dd * r.risk_px
            tp = entry + dd * r.rr * r.risk_px
            iend = min(i0 + (r.iend - r.i0), n - 1)
            res = C.simulate(inst, i0, entry, stop, tp, dd, iend, False)
            acc.append(res["R"] - r.cost_R)
        out[rep] = np.nanmean(acc)
    return out


# ---------------------------------------------------------------------------
def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def max_dd(x: np.ndarray) -> float:
    eq = np.cumsum(x)
    peak = np.maximum.accumulate(np.r_[0.0, eq])[1:]
    return float((peak - eq).max()) if len(x) else 0.0


def longest_loss_streak(x: np.ndarray) -> int:
    best = cur = 0
    for v in x:
        cur = cur + 1 if v < 0 else 0
        best = max(best, cur)
    return best


def underwater_days(tr: pd.DataFrame) -> float:
    eq = tr["R_net"].cumsum().to_numpy()
    t = pd.DatetimeIndex(tr["t_exit"])
    peak_t = t[0]
    peak = 0.0
    best = 0.0
    for v, ti in zip(eq, t):
        if v >= peak:
            peak, peak_t = v, ti
        else:
            best = max(best, (ti - peak_t).days)
    return best


def breakeven_cost_pip(tr: pd.DataFrame) -> float:
    """mean(R - c / risk_pip) = 0 -> c (pip)."""
    inv = (1 / tr["risk_pip"]).mean()
    return float(tr["R"].mean() / inv) if inv > 0 else np.nan


def metrics(tr: pd.DataFrame, mc_reps: int = 1000, seed: int = 0) -> dict:
    tr = tr.sort_values("t_entry")
    x = tr["R_net"].to_numpy()
    n = len(x)
    k = int(np.nansum(tr["hit"]))
    lo, hi = wilson(k, n)
    yrs = tr.groupby(tr["t_entry"].dt.year)["R_net"].sum()
    q = tr.groupby(tr["t_entry"].dt.to_period("Q").astype(str))["R_net"].sum()
    mon = tr.groupby(tr["t_entry"].dt.to_period("M").astype(str)).agg(R=("R_net", "sum"), n=("hit", "size"),
                                                                      wr=("hit", "mean"))
    srt = np.sort(x)
    rng = np.random.default_rng(seed)
    dds = np.array([max_dd(rng.permutation(x)) for _ in range(mc_reps)]) if n > 1 else np.array([0.0])
    lss = np.array([longest_loss_streak(rng.permutation(x)) for _ in range(min(mc_reps, 300))]) if n > 1 else np.array([0])
    span_years = max((tr["t_entry"].max() - tr["t_entry"].min()).days / 365.25, 1e-9) if n > 1 else np.nan
    pos, neg = x[x > 0].sum(), -x[x < 0].sum()
    r = {"n": n, "trades_per_year": n / 6.0, "wr": k / n if n else np.nan, "wr_lo": lo, "wr_hi": hi,
         "be_wr": float(np.nanmean(1 / (1 + tr["rr"]))), "rr_med": float(tr["rr"].median()),
         "R_gross_mean": float(tr["R"].mean()), "R_net_mean": float(x.mean()) if n else np.nan,
         "R_net_med": float(np.median(x)) if n else np.nan, "R_net_sum": float(x.sum()),
         "noTop2_sum": float(srt[:-2].sum()) if n > 2 else np.nan, "PF": float(pos / neg) if neg > 0 else np.nan,
         "R_per_month": float(x.sum() / 72.0), "years_pos": f"{int((yrs > 0).sum())}/{len(yrs)}",
         "quarters_pos": f"{int((q > 0).sum())}/{len(q)}", "maxDD_R": max_dd(x),
         "mc_dd95": float(np.percentile(dds, 95)), "mc_dd99": float(np.percentile(dds, 99)),
         "loss_streak": longest_loss_streak(x), "mc_ls95": float(np.percentile(lss, 95)),
         "underwater_days": underwater_days(tr) if n else np.nan,
         "breakeven_cost_pip": breakeven_cost_pip(tr), "cost_pip_med": float((tr["cost_R"] * tr["risk_pip"]).median()),
         "sr_trade": float(x.mean() / x.std(ddof=1)) if n > 2 and x.std(ddof=1) > 0 else np.nan,
         "skew": float(st.skew(x)) if n > 2 else np.nan, "kurt": float(st.kurtosis(x, fisher=False)) if n > 3 else np.nan,
         "months_wr_ge75": float((mon["wr"] >= 0.75).mean()) if len(mon) else np.nan,
         "month_wr_min": float(mon["wr"].min()) if len(mon) else np.nan,
         "month_R_med": float(mon["R"].median()) if len(mon) else np.nan,
         "span_years": span_years}
    for mult in (0.0, 0.5, 2.0):
        r[f"R_net_cost{mult:g}x"] = float((tr["R"] - mult * tr["cost_R"]).mean())
    for side, s in (("long", tr[tr.d == 1]), ("short", tr[tr.d == -1])):
        r[f"{side}_n"] = len(s)
        r[f"{side}_R_net"] = float(s["R_net"].mean()) if len(s) else np.nan
        r[f"{side}_wr"] = float(s["hit"].mean()) if len(s) else np.nan
    return r


def dsr(sr: float, n: int, skew: float, kurt: float, sr_var: float, n_trials: int) -> float:
    """Deflated Sharpe Ratio (Bailey & López de Prado 2014), işlem başına Sharpe."""
    if not np.isfinite(sr) or n < 3 or not np.isfinite(sr_var) or sr_var <= 0:
        return np.nan
    g = 0.5772156649
    z = st.norm.ppf
    sr0 = np.sqrt(sr_var) * ((1 - g) * z(1 - 1 / n_trials) + g * z(1 - 1 / (n_trials * np.e)))
    den = np.sqrt(max(1 - skew * sr + (kurt - 1) / 4 * sr * sr, 1e-12))
    return float(st.norm.cdf((sr - sr0) * np.sqrt(n - 1) / den))


def window_wr(tr: pd.DataFrame, n_win: int = 17, months: int = 6) -> dict:
    """İddia kıyası: kayan 17 işlemlik ve 6 aylık pencerelerde WR."""
    tr = tr.sort_values("t_entry")
    h = tr["hit"].to_numpy()
    out = {}
    if len(h) >= n_win:
        w = np.convolve(h, np.ones(n_win), "valid") / n_win
        out.update({"win17_max": float(w.max()), "win17_med": float(np.median(w)),
                    "win17_ge_8824": float((w >= 15 / 17 - 1e-9).mean())})
    m = tr.set_index(pd.DatetimeIndex(tr["t_entry"]).tz_convert(None)).sort_index()
    starts = pd.date_range("2020-01-01", "2025-07-01", freq="MS")
    wr6 = []
    for s in starts:
        g = m.loc[s:s + pd.DateOffset(months=months) - pd.Timedelta(seconds=1), "hit"]
        if len(g) >= 10:
            wr6.append(g.mean())
    if wr6:
        out.update({"win6m_min": float(min(wr6)), "win6m_max": float(max(wr6)),
                    "win6m_ge75": float(np.mean(np.array(wr6) >= 0.75))})
    return out
