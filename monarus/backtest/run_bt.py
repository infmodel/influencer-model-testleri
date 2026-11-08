"""Monarus backtest koşusu. Çıktılar out/: trades.parquet, summary.csv, perm.csv, claims.json, meta.json"""
from __future__ import annotations

import json
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

import bt
from bt import C, m_mc

OUT = bt.HERE / "out"
OUT.mkdir(exist_ok=True)
REPS = 200
CLAIM_MB = ["GBPUSD", "AUDUSD", "USDJPY"]


def work(name: str):
    inst = m_mc.load_nq() if name == "NQ" else C.load_inst(name)
    groups = bt.detect_nq(inst) if name == "NQ" else bt.detect_all(inst)
    if name == "NQ":
        m_mc.rth_days(inst)
    trades, perms = [], {}
    for b, evs in groups:
        if not evs:
            continue
        variants = [False, True] if name == "NQ" else [False]
        for be in variants:
            tr = pd.DataFrame(bt.sequential(inst, evs, b, be=be))
            if tr.empty:
                continue
            key = (tr["model"].iat[0], b, name)
            perms[key] = bt.random_entry(inst, tr, b, REPS, seed=sum(map(ord, "|".join(key))))
            trades.append(tr)
    return pd.concat(trades, ignore_index=True), perms


def main():
    t0 = time.time()
    names = C.ALL7 + ["NQ"]
    with ProcessPoolExecutor(max_workers=8) as ex:
        res = list(ex.map(work, names))
    trades = pd.concat([r[0] for r in res], ignore_index=True)
    perms = {}
    for r in res:
        perms.update(r[1])
    trades.to_parquet(OUT / "trades.parquet")
    print("işlemler hazır", len(trades), round(time.time() - t0), "sn", flush=True)

    rows = []
    for (model, b, inst), g in trades.groupby(["model", "boundary", "inst"]):
        m = bt.metrics(g)
        dist = perms[(model, b, inst)]
        m.update({"model": model, "boundary": b, "inst": inst, "perm_mean": float(dist.mean()),
                  "perm_z": float((m["R_net_mean"] - dist.mean()) / dist.std()) if dist.std() > 0 else np.nan,
                  "perm_p": float((np.sum(dist >= m["R_net_mean"]) + 1) / (len(dist) + 1))})
        rows.append(m)
    # havuzlar
    for (model, b), g0 in trades.groupby(["model", "boundary"]):
        pools = []
        if g0["inst"].nunique() > 1:
            pools.append(("POOL", g0))
        if model.startswith("MB"):
            pools.append(("POOL_CLAIM", g0[g0.inst.isin(CLAIM_MB)]))
        for pname, g in pools:
            m = bt.metrics(g)
            parts = [(perms[(model, b, i)], len(gi)) for i, gi in g.groupby("inst")]
            dist = sum(d * n for d, n in parts) / sum(n for _, n in parts)
            m.update({"model": model, "boundary": b, "inst": pname, "perm_mean": float(dist.mean()),
                      "perm_z": float((m["R_net_mean"] - dist.mean()) / dist.std()) if dist.std() > 0 else np.nan,
                      "perm_p": float((np.sum(dist >= m["R_net_mean"]) + 1) / (len(dist) + 1))})
            rows.append(m)
    sm = pd.DataFrame(rows)
    single = sm[~sm.inst.str.startswith("POOL")]
    # SR varyansı yalnız n >= 30 anahtarlardan (birkaç işlemlik anahtarlar uç SR üretir); N = tüm tekil anahtarlar
    sr_var = float(single.loc[single.n >= 30, "sr_trade"].var())
    n_trials = int(len(single))
    sm["dsr"] = [bt.dsr(r.sr_trade, r.n, r.skew, r.kurt, sr_var, n_trials) for r in sm.itertuples()]
    yrs = sm["years_pos"].str.split("/", expand=True).astype(int)
    sm["pass_profit"] = ((sm.R_net_mean > 0) & ((sm.R_net_med > 0) | (sm.rr_med >= 1)) & (sm.noTop2_sum > 0)
                         & (sm.perm_p < 0.05) & (sm.dsr > 0.95) & (yrs[0] >= 4)
                         & (sm.breakeven_cost_pip >= 2 * sm.cost_pip_med))
    cols = ["model", "boundary", "inst"] + [c for c in sm.columns if c not in ("model", "boundary", "inst")]
    sm[cols].to_csv(OUT / "summary.csv", index=False)

    # iddia kıyasları
    claims = {}
    for model in ("MB-v", "MB-s", "MB-h0"):
        g = trades[(trades.model == model) & trades.inst.isin(CLAIM_MB)]
        claims[f"{model}|POOL_CLAIM"] = bt.window_wr(g)
        for i in CLAIM_MB:
            claims[f"{model}|{i}"] = bt.window_wr(g[g.inst == i])
    for model in sorted(trades.model.unique()):
        if model.startswith(("MF", "MD", "MC")):
            g = trades[(trades.model == model) & (trades.boundary == "ny17")]
            claims[f"{model}|POOL"] = bt.window_wr(g)
    (OUT / "claims.json").write_text(json.dumps(claims, indent=1, ensure_ascii=False))
    monthly = trades.assign(month=trades.t_entry.dt.to_period("M").astype(str)).groupby(
        ["model", "boundary", "inst", "month"]).agg(n=("hit", "size"), tp=("hit", "sum"), R_net=("R_net", "sum"))
    monthly.to_csv(OUT / "monthly.csv")
    meta = {"n_trades": int(len(trades)), "n_keys_single": n_trials, "n_rows": int(len(sm)),
            "sr_var": sr_var, "perm_reps": REPS, "n_pass_profit": int(sm.pass_profit.sum()),
            "runtime_s": round(time.time() - t0)}
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
