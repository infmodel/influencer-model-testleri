"""Adım 0 olay çalışması (backtest değil). Yalnızca IS 2020-2025.

Çıktılar adim0/out/: events_{SYM}.parquet, stats_{SYM}.csv, years_{SYM}.csv,
feature_ic_{SYM}.csv, mda_{SYM}.csv, mfe_mae_{SYM}.csv, sonuclar.md, meta.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "faz0"))

import events as E  # noqa: E402
from dreyko_data import load_is  # noqa: E402

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
HZ = [f"h{h}" for h in E.HORIZONS] + ["noon"]
FEATS = ["smt", "makro", "gap_atr", "on_range_atr", "prev_ret_atr", "pm_range_atr", "pos_pm",
         "fvg_size_atr", "mins_since_open", "wait_min", "sweep_depth_atr"]
SUBSETS = {
    "tümü": lambda d: d,
    "SMT var": lambda d: d[d.smt == 1],
    "SMT yok": lambda d: d[d.smt == 0],
    "makro içi": lambda d: d[d.makro],
    "makro dışı": lambda d: d[~d.makro],
    "long": lambda d: d[d.d == 1],
    "short": lambda d: d[d.d == -1],
}


def prepare(sym):
    df = load_is(sym, ["open", "high", "low", "close"])
    assert df.index.max() < pd.Timestamp("2026-01-01")
    return E.build_days(df), E.daily_context(df)


def baseline(days, ctx):
    """Koşulsuz: her gün, her giriş dakikasında (09:30-11:09) bar açılışından long getiri / ATR."""
    acc = {}
    n_days = 0
    for date, day in days.items():
        if date not in ctx.index:
            continue
        atr = ctx.at[date, "atr"]
        if not np.isfinite(atr) or day.idx_at(E.RTH_OPEN) < 0:
            continue
        n_days += 1
        for m in range(E.RTH_OPEN, E.DEADLINE + 1):
            k = day.idx_at(m)
            if k < 0:
                continue
            t0 = int(day.tm[k])
            T = {f"h{h}": t0 + h for h in E.HORIZONS}
            T["noon"] = day.base + E.NOON
            for name, t in T.items():
                px = E.price_at(day, t, k)
                if np.isfinite(px):
                    acc.setdefault((m, name), []).append((px - day.o[k]) / atr)
    base = {k: float(np.mean(v)) for k, v in acc.items()}
    return base, n_days


def run_symbol(sym, days, ctx, other_days):
    rows = []
    for date, day in days.items():
        if date not in ctx.index:
            continue
        c = ctx.loc[date].to_dict()
        for ev in E.detect_day(day, other_days.get(date), c):
            em = int(day.mod[ev.entry_idx])
            rec = {"sym": sym, "date": date, "year": date.year, "event": ev.event, "variant": ev.variant,
                   "d": ev.d, "entry_kind": ev.entry_kind, "entry_mod": em, "entry_px": ev.entry_px,
                   "makro": E.MACRO[0] <= em <= E.MACRO[1]}
            rec.update(ev.feats)
            rec.update(E.label(day, ev, c["atr"]))
            rows.append(rec)
    ev = pd.DataFrame(rows)
    ev["key"] = ev.event + np.where(ev.variant == "-", "", "_" + ev.variant)
    return ev


def tstat(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 5 or x.std(ddof=1) == 0:
        return n, np.nan, np.nan, np.nan, np.nan, np.nan
    t = x.mean() / (x.std(ddof=1) / np.sqrt(n))
    p = 2 * st.t.sf(abs(t), n - 1)
    return n, x.mean(), np.median(x), (x > 0).mean(), t, p


def bh(p):
    p = np.asarray(p, float)
    q = np.full_like(p, np.nan)
    ok = np.isfinite(p)
    pv = p[ok]
    m = len(pv)
    o = np.argsort(pv)
    r = pv[o] * m / np.arange(1, m + 1)
    r = np.minimum.accumulate(r[::-1])[::-1]
    out = np.empty(m)
    out[o] = np.minimum(r, 1)
    q[ok] = out
    return q


def stats_table(ev):
    recs = []
    for key, g in ev.groupby("key"):
        for sname, f in SUBSETS.items():
            s = f(g)
            for h in HZ:
                n, mu, med, hit, t, p = tstat(s[f"dret_{h}"])
                _, xmu, _, _, xt, xp = tstat(s[f"xret_{h}"])
                yrs = s.groupby("year")[f"dret_{h}"].mean()
                same = int((np.sign(yrs) == np.sign(mu)).sum()) if np.isfinite(mu) else 0
                recs.append({"key": key, "subset": sname, "horizon": h, "n": n, "mean": mu, "median": med,
                             "hit": hit, "t": t, "p": p, "x_mean": xmu, "x_t": xt, "x_p": xp,
                             "years_same_sign": f"{same}/{len(yrs)}"})
    df = pd.DataFrame(recs)
    df["q_bh"] = bh(df.p)
    m = df.p.notna().sum()
    df["p_bonf"] = np.minimum(df.p * m, 1)
    df["x_q_bh"] = bh(df.x_p)
    return df


def year_table(ev):
    t = ev.pivot_table(index=["key", "year"], values=["dret_h60", "dret_noon"], aggfunc=["mean", "count"])
    t.columns = [f"{a}_{b}" for a, b in t.columns]
    return t.reset_index()


def mfe_table(ev):
    q = [0.25, 0.5, 0.75, 0.9]
    recs = []
    for key, g in ev.groupby("key"):
        r = {"key": key, "n": len(g)}
        for col in ("mfe_noon", "mae_noon"):
            for qq in q:
                r[f"{col}_q{int(qq * 100)}"] = g[col].quantile(qq)
        recs.append(r)
    return pd.DataFrame(recs)


def feature_ic(ev):
    recs = []
    for key, g in ev.groupby("key"):
        for f in FEATS:
            if f not in g or g[f].notna().sum() < 30 or g[f].nunique() < 2:
                continue
            s = g[[f, "dret_noon"]].dropna()
            rho, p = st.spearmanr(s[f].astype(float), s.dret_noon)
            recs.append({"key": key, "feature": f, "n": len(s), "ic": rho, "p": p})
    df = pd.DataFrame(recs)
    df["q_bh"] = bh(df.p)
    return df


def mda(ev):
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.inspection import permutation_importance
    from sklearn.metrics import roc_auc_score
    recs, perf = [], []
    for key, g in ev.groupby("key"):
        g = g[np.isfinite(g.dret_noon)]
        if len(g) < 300:
            continue
        cols = [f for f in FEATS if f in g and g[f].notna().mean() > 0.5 and g[f].nunique() > 1]
        X = g[cols].astype(float).to_numpy()
        y = (g.dret_noon > 0).astype(int).to_numpy()
        yrs = g.year.to_numpy()
        oof = np.full(len(g), np.nan)
        imps = []
        for yr in np.unique(yrs):          # Leave-One-Year-Out; etiketler gün içi biter, purge gerekmez
            tr, te = yrs != yr, yrs == yr
            if te.sum() < 30 or len(np.unique(y[te])) < 2:
                continue
            mdl = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200,
                                                 min_samples_leaf=40, random_state=0)
            mdl.fit(X[tr], y[tr])
            oof[te] = mdl.predict_proba(X[te])[:, 1]
            pi = permutation_importance(mdl, X[te], y[te], scoring="roc_auc", n_repeats=20, random_state=0)
            imps.append(pi.importances_mean)
        ok = np.isfinite(oof)
        auc = roc_auc_score(y[ok], oof[ok])
        ic = st.spearmanr(oof[ok], g.dret_noon.to_numpy()[ok])[0]
        perf.append({"key": key, "n": int(ok.sum()), "oof_auc": auc, "oof_ic": ic})
        imps = np.array(imps)
        for j, c in enumerate(cols):
            recs.append({"key": key, "feature": c, "mda_mean": imps[:, j].mean(),
                         "mda_std": imps[:, j].std(), "folds_pos": f"{(imps[:, j] > 0).sum()}/{len(imps)}"})
    return pd.DataFrame(recs), pd.DataFrame(perf)


def main():
    print("veri yükleniyor...")
    nq_days, nq_ctx = prepare("NQ")
    es_days, es_ctx = prepare("ES")
    meta = {"is_range": "2020-01-01..2025-12-31", "tests": {}}
    md = ["# Adım 0 ham sonuçlar (otomatik)\n"]
    for sym, d_, c_, o_ in (("NQ", nq_days, nq_ctx, es_days), ("ES", es_days, es_ctx, nq_days)):
        print(sym, "baseline...")
        base, n_days = baseline(d_, c_)
        print(sym, "olaylar...")
        ev = run_symbol(sym, d_, c_, o_)
        for h in HZ:
            b = np.array([base.get((m, h), np.nan) for m in ev.entry_mod])
            ev[f"xret_{h}"] = ev.d * (ev[f"ret_{h}"] - b)
        ev.to_parquet(OUT / f"events_{sym}.parquet")
        s = stats_table(ev)
        s.to_csv(OUT / f"stats_{sym}.csv", index=False)
        year_table(ev).to_csv(OUT / f"years_{sym}.csv", index=False)
        mfe_table(ev).to_csv(OUT / f"mfe_mae_{sym}.csv", index=False)
        fi = feature_ic(ev)
        fi.to_csv(OUT / f"feature_ic_{sym}.csv", index=False)
        no_mar20 = ev[~((ev.date >= "2020-03-01") & (ev.date < "2020-04-01"))]
        s2 = stats_table(no_mar20)
        s2.to_csv(OUT / f"stats_{sym}_noMar2020.csv", index=False)
        if sym == "NQ":
            imp, perf = mda(ev)
            imp.to_csv(OUT / f"mda_{sym}.csv", index=False)
            perf.to_csv(OUT / f"mda_perf_{sym}.csv", index=False)
        meta["tests"][sym] = {"stats_raw": int(s.p.notna().sum()), "stats_excess": int(s.x_p.notna().sum()),
                              "feature_ic": int(fi.p.notna().sum())}
        meta[f"{sym}_eligible_days"] = n_days
        meta[f"{sym}_events"] = ev.groupby("key").size().to_dict()
        pd.Series({f"{k}|{h}": v for (k, h), v in base.items()}).to_csv(OUT / f"baseline_{sym}.csv")
        md.append(f"## {sym}: uygun gün {n_days}\n")
        cnt = ev.groupby("key").agg(n=("d", "size"), long=("d", lambda x: (x == 1).sum()),
                                     smt=("smt", "mean"), makro=("makro", "mean"))
        cnt["gün_oranı"] = cnt.n / n_days
        md.append("```\n" + cnt.round(3).to_string() + "\n```\n")
        top = s[s.subset == "tümü"][["key", "horizon", "n", "mean", "median", "hit", "t", "p", "q_bh",
                                       "x_mean", "x_t", "years_same_sign"]]
        md.append("```\n" + top.round(4).to_string(index=False) + "\n```\n")
    (OUT / "sonuclar.md").write_text("\n".join(md))
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2, default=str, ensure_ascii=False))
    print(json.dumps(meta["tests"], indent=1))


if __name__ == "__main__":
    main()
