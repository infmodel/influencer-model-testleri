"""32 ön kayıtlı varyant: NQ (kural kurulur) + ES (aynen). Yalnızca IS 2020-2025."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "adim0"))
sys.path.insert(0, str(HERE.parent / "faz0"))

import bt  # noqa: E402
import events as E  # noqa: E402
from dreyko_data import load_is  # noqa: E402
from run_adim0 import bh  # noqa: E402

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
HYP = {("FPFVG_form", "A"): "H1-A", ("FPFVG_form", "B"): "H1-B", ("IFVG", "-"): "H2", ("TSCISD", "-"): "H2b"}
FILTERS = {"filtresiz": lambda t: t, "SMT": lambda t: t[t.smt == 1],
           "makro": lambda t: t[t.makro], "SMT+makro": lambda t: t[(t.smt == 1) & t.makro]}


def load(sym):
    df = load_is(sym, ["open", "high", "low", "close", "adj_factor"])
    assert df.index.max() < pd.Timestamp("2026-01-01")
    mod = df.index.hour * 60 + df.index.minute
    adj = df[mod == E.RTH_OPEN].groupby("session_date").adj_factor.first()
    return E.build_days(df), E.daily_context(df), adj


def trades_for(sym, days, ctx, adj, other_days, through_ticks=1):
    rows = []
    for date, day in days.items():
        if date not in ctx.index or date not in adj.index:
            continue
        other = other_days.get(date)
        for ev in E.detect_day(day, other, ctx.loc[date].to_dict()):
            h = HYP.get((ev.event, ev.variant))
            if h is None:
                continue
            for tg in ("L", "R"):
                t = bt.make_trade(sym, day, other, ev, float(adj[date]), tg, through_ticks)
                if t is not None:
                    t.update(hyp=h, target=tg)
                    rows.append(t)
    return pd.DataFrame(rows)


def evaluate(tr):
    recs = []
    for (h, tg), g in tr.groupby(["hyp", "target"]):
        for fname, f in FILTERS.items():
            m = bt.metrics(f(g))
            m.update(hyp=h, target=tg, filter=fname)
            recs.append(m)
    r = pd.DataFrame(recs)
    r["perm_q"] = bh(r.perm_p.to_numpy())
    first = ["hyp", "target", "filter"]
    return r[first + [c for c in r.columns if c not in first]]


def main():
    nq = load("NQ")
    es = load("ES")
    res = {}
    for sym, (d_, c_, a_), od in (("NQ", nq, es[0]), ("ES", es, nq[0])):
        tr = trades_for(sym, d_, c_, a_, od)
        tr.to_parquet(OUT / f"trades_{sym}.parquet")
        r = evaluate(tr)
        r.to_csv(OUT / f"results_{sym}.csv", index=False)
        res[sym] = r
        if sym == "NQ":     # duyarlılık: dokunuşta dolum (aile dışı)
            tr0 = trades_for(sym, d_, c_, a_, od, through_ticks=0)
            tr0 = tr0[tr0.hyp.str.startswith("H1")]
            s = evaluate(tr0)
            s = s[s["filter"] == "filtresiz"]
            s.to_csv(OUT / "sens_touchfill_NQ.csv", index=False)
            res["NQ_touch"] = s
    pd.set_option("display.width", 250)
    cols = ["hyp", "target", "filter", "n", "win", "avgR", "medR", "noTop2R", "PF", "usd", "maxDD_usd",
            "yrs_pos", "longR", "shortR", "be_cost_pts", "avg_risk_pts", "stop%", "tgt%", "time%", "perm_p", "perm_q"]
    for k, r in res.items():
        print(f"\n===== {k} =====")
        print(r[[c for c in cols if c in r]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
