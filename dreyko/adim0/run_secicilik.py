"""Seçicilik turu (ön kayıt: karar_gunlugu.md). Adım 0 olayları + etiketleri aynen, yalnız filtre eklenir."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "faz0"))

import events as E  # noqa: E402
import secicilik as S  # noqa: E402
from dreyko_data import load_is  # noqa: E402
from run_adim0 import HZ, bh, tstat  # noqa: E402

OUT = HERE / "out"
SUBS = {
    "F1": lambda g: g[g.F1],
    "F2": lambda g: g[g.F2],
    "F3": lambda g: g[g.F3],
    "F1∧F2 (A+)": lambda g: g[g.F1 & g.F2],
    "F1∧SMT (3 şart)": lambda g: g[g.F1 & (g.smt == 1)],
    "F1∧F2∧F3": lambda g: g[g.F1 & g.F2 & g.F3],
}


def add_flags(sym):
    df = load_is(sym, ["open", "high", "low", "close"])
    ctx = E.daily_context(df)
    sb = S.session_bars(df)
    lv = S.levels(sb, ctx["atr"])
    ev = pd.read_parquet(OUT / f"events_{sym}.parquet")
    fl = [S.flags(r.date, int(r.entry_mod), int(r.d), sb, lv.loc[r.date]) for r in ev.itertuples()]
    ev = pd.concat([ev.reset_index(drop=True), pd.DataFrame(fl)], axis=1)
    ev.to_parquet(OUT / f"events_{sym}_flags.parquet")
    return ev


def table(ev):
    recs = []
    for key, g in ev.groupby("key"):
        for sname, f in SUBS.items():
            s = f(g)
            for h in HZ:
                n, mu, med, hit, t, p = tstat(s[f"dret_{h}"])
                yrs = s.groupby("year")[f"dret_{h}"].mean()
                same = int((np.sign(yrs) == np.sign(mu)).sum()) if np.isfinite(mu) else 0
                recs.append({"key": key, "subset": sname, "horizon": h, "n": n, "mean": mu, "median": med,
                             "hit": hit, "t": t, "p": p, "years_same_sign": f"{same}/{len(yrs)}"})
    df = pd.DataFrame(recs)
    prim = (df.subset == "F1∧F2 (A+)") & (df.horizon == "noon")
    df["family"] = np.where(prim, "birincil", "ikincil")
    df["q_bh"] = np.nan
    for fam in ("birincil", "ikincil"):
        m = df.family == fam
        df.loc[m, "q_bh"] = bh(df.loc[m, "p"].to_numpy())
    return df


def main():
    meta = {}
    res = {}
    for sym in ("NQ", "ES"):
        ev = add_flags(sym)
        t = table(ev)
        t.to_csv(OUT / f"secicilik_{sym}.csv", index=False)
        res[sym] = t
        meta[sym] = {"flag_rates": ev.groupby("key")[["F1", "F2", "F3"]].mean().round(3).to_dict(),
                     "tests": {f: int((t.family == f).sum() - t[t.family == f].p.isna().sum())
                               for f in ("birincil", "ikincil")}}
    (OUT / "secicilik_meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    pd.set_option("display.width", 200)
    for sym, t in res.items():
        print(f"\n=== {sym} birincil (F1∧F2, 12:00) ===")
        print(t[t.family == "birincil"].drop(columns=["family"]).round(4).to_string(index=False))
        print(f"--- {sym} ikincil: en küçük 10 p ---")
        print(t[t.family == "ikincil"].sort_values("p").head(10).drop(columns=["family"]).round(4).to_string(index=False))
    print(json.dumps({s: m["tests"] for s, m in meta.items()}))


if __name__ == "__main__":
    main()
