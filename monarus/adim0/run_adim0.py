"""Adım 0 olay çalışması (backtest değil), Monarus MA–MF. Ön kayıt: on_kayit.md. Yalnız IS 2020-2025.

Çıktılar out/: events_<model>.parquet, ma_days.parquet, stats.csv, ma_stats.csv, mda.csv, mda_perf.csv,
mc_h0.csv, meta.json
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from scipy import stats as st

import common as C
import m_ma
import m_mb
import m_mc
import m_md
import m_me
import m_mf

OUT = C.HERE / "out"
OUT.mkdir(exist_ok=True)
BOUNDS = ("ny17", "tr")
CLAIM_MB = ["GBPUSD", "AUDUSD", "USDJPY"]


# ---------------------------------------------------------------------------
def tstat(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 5 or x.std(ddof=1) == 0:
        return n, (x.mean() if n else np.nan), np.nan, np.nan
    t = x.mean() / (x.std(ddof=1) / np.sqrt(n))
    return n, x.mean(), t, 2 * st.t.sf(abs(t), n - 1)


def bh(p):
    p = np.asarray(p, float)
    q = np.full_like(p, np.nan)
    ok = np.isfinite(p)
    pv = p[ok]
    m = len(pv)
    if m == 0:
        return q
    o = np.argsort(pv)
    r = pv[o] * m / np.arange(1, m + 1)
    r = np.minimum.accumulate(r[::-1])[::-1]
    out = np.empty(m)
    out[o] = np.minimum(r, 1)
    q[ok] = out
    return q


def years_same(g, col):
    y = g.groupby("year")[col].agg(["mean", "size"])
    y = y[y["size"] >= 5]
    mu = g[col].mean()
    if not np.isfinite(mu) or len(y) == 0:
        return "0/0"
    return f"{int((np.sign(y['mean']) == np.sign(mu)).sum())}/{len(y)}"


# ---------------------------------------------------------------------------
def inst_jobs(name: str) -> list[dict]:
    """Bir enstrümanın bütün işlem tipi olayları (etiketli)."""
    inst = C.load_inst(name)
    out = []

    def add(evs, boundary):
        if not evs:
            return
        d = C.days(inst, boundary)
        dom = C.day_of_minute(inst, boundary)
        dn = C.days(inst, "ny17")
        domn = C.day_of_minute(inst, "ny17")
        for e in evs:
            if not (e["d"] * (e["entry"] - e["stop"]) > 0 and e["d"] * (e["tp"] - e["entry"]) > 0):
                raise ValueError(f"geçersiz geometri: {e}")
            rec = {k: v for k, v in e.items() if k not in ("fill_partial",)}
            rec.update(C.label_trade(inst, e, dn, domn))      # ATR/gün sonu: ny17 günü (ortak ölçek)
            k = dom[e["i0"]]
            rec.update({"inst": name, "boundary": boundary, "year": pd.Timestamp(e["date"]).year,
                        "dow": pd.Timestamp(e["date"]).dayofweek,
                        "prev_range_atr": (d["high"].iat[k - 1] - d["low"].iat[k - 1]) / rec["atr"] if k > 0 else np.nan,
                        "t_entry": pd.Timestamp(inst.t[e["i0"]], tz="UTC")})
            out.append(rec)

    for b in BOUNDS:
        add(m_ma.ma_t_events(inst, b), b)
        add(m_me.me1_events(inst, b), b)
        add(m_me.me1_events(inst, b, filtered=False), b)
        add(m_me.me2_events(inst, b), b)
        p15 = m_mf.Piv15(inst, 15)
        for mode in ("1", "1k", "n"):
            add(m_mf.mf_events(inst, b, mode, p15), b)
        if b == "ny17":
            add(m_mf.mf_events(inst, b, "1", p15, sweep_atr=True), b)
        p30 = m_mf.Piv15(inst, 30)
        for htf in ("4S", "1G"):
            for en in ("a", "b"):
                add(m_md.md_events(inst, b, htf, en, piv30=p30), b)
            add(m_md.md_events(inst, b, htf, "a", rr_filter=False, piv30=p30), b)
        if b == "ny17":
            for en in ("a", "b"):
                add(m_md.md_events(inst, b, None, en, piv30=p30), b)
    if name in C.FX6:
        f = m_mb.mb_features(inst)
        for v in ("v", "s", "h0"):
            add(m_mb.mb_events(inst, v, f), "ny17")
    base = {b: C.baseline_minute(inst, "ny17") for b in ("ny17",)}
    df = pd.DataFrame(out)
    if len(df):
        df = C.add_excess(df, base["ny17"])
    ma = pd.concat([m_ma.ma_days(inst, b).assign(inst=name, boundary=b) for b in BOUNDS])
    return {"events": df, "ma": ma}


def nq_jobs() -> pd.DataFrame:
    inst = m_mc.load_nq()
    dn = C.days(inst, "ny17")
    domn = C.day_of_minute(inst, "ny17")
    rows = []
    for v in ("A", "B"):
        for sp in (0.005, 0.01):
            for e in m_mc.mc_events(inst, v, sp):
                rec = dict(e)
                rec.pop("fill_partial", None)
                rec.update(C.label_trade(inst, e, dn, domn))
                rec["R_be"] = m_mc.simulate_be(inst, e["i0"], e["entry"], e["stop"], e["tp"], e["d"], e["iend"],
                                               e["fill_partial"])
                rec["R_be_net"] = rec["R_be"] - rec["cost_R"]
                rec.update({"inst": "NQ", "boundary": "ny17", "year": e["date"].year, "dow": e["date"].dayofweek,
                            "prev_range_atr": np.nan, "t_entry": pd.Timestamp(inst.t[e["i0"]], tz="UTC")})
                rows.append(rec)
    df = pd.DataFrame(rows)
    df = C.add_excess(df, C.baseline_minute(inst, "ny17"))
    # H0: rastgele dakika ve yön (yalnız %1 stop varyantlarında; %0.5 alt kümesi)
    h0 = []
    for key, g in df.groupby("model"):
        dist = m_mc.h0_random(inst, g, reps=500, seed=sum(map(ord, key)))
        obs = g["R"].mean()
        h0.append({"model": key, "n": len(g), "obs_meanR": obs, "h0_mean": dist.mean(), "h0_sd": dist.std(),
                   "p_perm": float((np.sum(dist >= obs) + 1) / (len(dist) + 1)),
                   "z": float((obs - dist.mean()) / dist.std())})
    return df, pd.DataFrame(h0)


# ---------------------------------------------------------------------------
def trade_stats(ev: pd.DataFrame) -> pd.DataFrame:
    recs = []
    pools = {"POOL_ALL": lambda g: g}
    for (model, b), g0 in ev.groupby(["model", "boundary"]):
        groups = [(i, g) for i, g in g0.groupby("inst")]
        if g0["inst"].nunique() > 1:
            groups.append(("POOL", g0))
        if model.startswith("MB-"):
            groups.append(("POOL_CLAIM", g0[g0.inst.isin(CLAIM_MB)]))
        for inst, g in groups:
            for sub, s in (("tümü", g), ("long", g[g.d == 1]), ("short", g[g.d == -1])):
                if len(s) == 0:
                    continue
                n, mu, t, p = tstat(s["R_net"])
                _, mug, tg, pg = tstat(s["R"])
                _, md_, tdr, pdr = tstat(s["dR"])
                _, mx, tx, px = tstat(s["x_eod"])
                r = {"model": model, "boundary": b, "inst": inst, "subset": sub, "n": n,
                     "hit": s["hit"].mean(), "mhit": s["mhit"].mean(), "rr_med": s["rr"].median(),
                     "be_wr": float(np.nanmean(1 / (1 + s["rr"]))),
                     "R_mean": mug, "R_net_mean": mu, "R_net_med": s["R_net"].median(), "t": t, "p": p,
                     "dR_mean": md_, "dR_t": tdr, "dR_p": pdr, "x_eod": mx, "x_eod_p": px,
                     "years": years_same(s, "R_net"), "cost_R_med": s["cost_R"].median(),
                     "stop_atr_med": s["stop_atr"].median(), "resolved": s["resolved"].mean()}
                if "R_be_net" in s and s["R_be_net"].notna().any():
                    _, mbe, tbe, pbe = tstat(s["R_be_net"])
                    r.update({"R_be_net_mean": mbe, "R_be_p": pbe})
                recs.append(r)
    return pd.DataFrame(recs)


def ma_stats(ma: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for (inst, b), g in ma.groupby(["inst", "boundary"]):
        uH, uL = g["hitH"].mean(), g["hitL"].mean()
        mret = g["ret_cc"].mean()
        bz = g[g.bias != 0].copy()
        bz["exp"] = np.where(bz.bias == 1, uH, uL)
        bz["xret"] = bz.bias * (bz.ret_cc - mret)
        subs = {"tümü": bz, "flow": bz[bz.state.str.startswith("flow")], "crt": bz[bz.state.str.startswith("crt")],
                "long": bz[bz.bias == 1], "short": bz[bz.bias == -1]}
        for sname, s in subs.items():
            n, md1, t1, p1 = tstat(s.hit_bias - s.hit_opp)
            _, md2, t2, p2 = tstat(s.first_bias - 0.5)
            _, md3, t3, p3 = tstat(s.hit_bias - s.exp)
            _, md4, t4, p4 = tstat(s.xret)
            _, md5, t5, p5 = tstat(s.hit_bias - s.hit_mirror)     # post-hoc ayna-mesafe kontrolü
            recs.append({"inst": inst, "boundary": b, "subset": sname, "n": n, "days_all": len(g),
                         "hit_bias": s.hit_bias.mean(), "hit_opp": s.hit_opp.mean(), "uncond": s.exp.mean(),
                         "first_bias": s.first_bias.mean(), "diff": md1, "p_diff": p1,
                         "p_first": p2, "x_uncond": md3, "p_uncond": p3, "xret": md4, "p_xret": p4,
                         "hit_mirror": s.hit_mirror.mean(), "diff_mirror": md5, "p_mirror": p5,
                         "tgt_dist_atr_med": s.tgt_dist_atr.median(),
                         "years_diff": years_same(s.assign(z=s.hit_bias - s.hit_opp), "z")})
    return pd.DataFrame(recs)


def mda(ev: pd.DataFrame):
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.inspection import permutation_importance
    from sklearn.metrics import roc_auc_score
    feats = ["stop_atr", "tr_hour", "dow", "d", "atr_pct", "prev_range_atr", "rr"]
    recs, perf = [], []
    ev = ev.assign(tr_hour=ev.tr_min // 60)
    for (model, b), g in ev[ev.boundary == "ny17"].groupby(["model", "boundary"]):
        g = g[np.isfinite(g.R_net)]
        if len(g) < 300:
            continue
        cols = [f for f in feats if g[f].notna().mean() > 0.5 and g[f].nunique() > 1]
        X = g[cols].astype(float).to_numpy()
        y = (g.R_net > 0).astype(int).to_numpy()
        yrs = g.year.to_numpy()
        oof = np.full(len(g), np.nan)
        imps = []
        for yr in np.unique(yrs):
            tr, te = yrs != yr, yrs == yr
            if te.sum() < 30 or len(np.unique(y[te])) < 2 or len(np.unique(y[tr])) < 2:
                continue
            mdl = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200,
                                                 min_samples_leaf=40, random_state=0)
            mdl.fit(X[tr], y[tr])
            oof[te] = mdl.predict_proba(X[te])[:, 1]
            pi = permutation_importance(mdl, X[te], y[te], scoring="roc_auc", n_repeats=10, random_state=0)
            imps.append(pi.importances_mean)
        ok = np.isfinite(oof)
        if ok.sum() < 100:
            continue
        perf.append({"model": model, "n": int(ok.sum()), "oof_auc": roc_auc_score(y[ok], oof[ok]),
                     "oof_ic": st.spearmanr(oof[ok], g.R_net.to_numpy()[ok])[0]})
        imps = np.array(imps)
        for j, c in enumerate(cols):
            recs.append({"model": model, "feature": c, "mda_mean": imps[:, j].mean(), "mda_std": imps[:, j].std(),
                         "folds_pos": f"{(imps[:, j] > 0).sum()}/{len(imps)}"})
    return pd.DataFrame(recs), pd.DataFrame(perf)


def main():
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=7) as ex:
        fut = {n: ex.submit(inst_jobs, n) for n in C.ALL7}
        fnq = ex.submit(nq_jobs)
        res = {n: f.result() for n, f in fut.items()}
        nq_ev, mc_h0 = fnq.result()
    print("olaylar hazır", round(time.time() - t0), "sn", flush=True)
    ev = pd.concat([r["events"] for r in res.values()] + [nq_ev], ignore_index=True)
    ma = pd.concat([r["ma"] for r in res.values()], ignore_index=True)
    for m, g in ev.groupby("model"):
        g.to_parquet(OUT / f"events_{m}.parquet")
    ma.to_parquet(OUT / "ma_days.parquet")
    mc_h0.to_csv(OUT / "mc_h0.csv", index=False)
    ts = trade_stats(ev)
    ms = ma_stats(ma)
    # tek havuzda çoklu test düzeltmesi: işlem tipi (R_net, ayna) + MA (4 test) + MC H0
    pcols = [("ts", "p"), ("ts", "dR_p"), ("ts", "x_eod_p"), ("ts", "R_be_p"),
             ("ms", "p_diff"), ("ms", "p_first"), ("ms", "p_uncond"), ("ms", "p_xret"), ("ms", "p_mirror")]
    allp = []
    for src, col in pcols:
        df = ts if src == "ts" else ms
        if col in df:
            allp.append(df[col].to_numpy())
    allp.append(mc_h0["p_perm"].to_numpy())
    flat = np.concatenate(allp)
    q = bh(flat)
    m_tests = int(np.isfinite(flat).sum())
    pos = 0
    for (src, col), arr in zip([c for c in pcols if c[1] in (ts if c[0] == "ts" else ms)], allp[:-1]):
        df = ts if src == "ts" else ms
        df[col.replace("p", "q", 1) if col == "p" else col + "_q"] = q[pos:pos + len(arr)]
        df[(col + "_bonf")] = np.minimum(arr * m_tests, 1)
        pos += len(arr)
    mc_h0["q"] = q[pos:pos + len(mc_h0)]
    ts.to_csv(OUT / "stats.csv", index=False)
    ms.to_csv(OUT / "ma_stats.csv", index=False)
    mc_h0.to_csv(OUT / "mc_h0.csv", index=False)
    imp, perf = mda(ev)
    imp.to_csv(OUT / "mda.csv", index=False)
    perf.to_csv(OUT / "mda_perf.csv", index=False)
    meta = {"is_range": "2020-01-01..2025-12-31", "n_tests_pooled": m_tests,
            "n_events": ev.groupby("model").size().to_dict(),
            "n_keys_trade": int(len(ts)), "n_rows_ma": int(len(ms)), "runtime_s": round(time.time() - t0)}
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False, default=str))
    print(json.dumps({k: meta[k] for k in ("n_tests_pooled", "n_keys_trade", "runtime_s")}))


if __name__ == "__main__":
    main()
