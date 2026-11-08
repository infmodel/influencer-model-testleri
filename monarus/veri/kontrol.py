"""Arguman: raw_klasoru SEMBOL(kucuk harf) alt_fiyat ust_fiyat. Temel kalite kontrolleri."""
import sys, glob
import pandas as pd, numpy as np
raw, s, lo, hi = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
tot = 0
for f in sorted(glob.glob(f"{raw}/{s}_*.parquet")):
    d = pd.read_parquet(f); tot += len(d)
    t = d.timestamp
    hl = (d.high < d.low).sum()
    oc = ((d.open > d.high) | (d.open < d.low) | (d.close > d.high) | (d.close < d.low)).sum()
    flat = ((d.open == d.high) & (d.high == d.low) & (d.low == d.close)).sum()
    gap = t.diff().dropna()
    wk = gap[(t.dt.dayofweek.iloc[1:] .values < 5) & (gap > pd.Timedelta(minutes=1)).values] if False else None
    # en uzun hafta ici bosluk: bosluk her iki ucu hafta ici (Pzt-Cum) ve haftasonu kapanisi disinda
    g = pd.DataFrame({"a": t.shift(1), "b": t}).dropna(); g["d"] = g.b - g.a
    g = g[g.d > pd.Timedelta(minutes=1)]
    g = g[~((g.a.dt.dayofweek == 4) & (g.b.dt.dayofweek == 6))]
    mg = g.sort_values("d").tail(1)
    print(f"{s} {f[-12:-8]} satir={len(d)} dtype={dict(d.dtypes.astype(str))['timestamp']} sirali={t.is_monotonic_increasing} mukerrer={t.duplicated().sum()} "
          f"NaN={int(d.isna().sum().sum())} high<low={hl} OC_aralik_disi={oc} duz={flat} min={d[['open','high','low','close']].min().min():.5f} max={d[['open','high','low','close']].max().max():.5f} "
          f"aralik_disi={(d[['open','high','low','close']].lt(lo)|d[['open','high','low','close']].gt(hi)).any(axis=1).sum()} "
          f"min_ts={t.min()} max_ts={t.max()} en_uzun_bosluk(Cum->Paz disi)={mg.d.iloc[0] if len(mg) else None} @ {mg.a.iloc[0] if len(mg) else ''}")
print("toplam", tot)
