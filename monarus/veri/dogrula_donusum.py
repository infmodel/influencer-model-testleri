"""Arguman: dogrulama_klasoru mevcut_parquet. Indirilen EURUSD gunlerini donustur, mevcut dosyayla karsilastir."""
import sys, os, glob, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
from donustur import decode_day, transform
folder, pq = sys.argv[1], sys.argv[2]
ex = pd.read_parquet(pq).set_index("timestamp")
parts, days = [], []
for f in sorted(glob.glob(folder + "/EURUSD/2023/*/*.bi5")):
    y, m, d = f.split("/")[-3:]; day = dt.date(int(y), int(m), int(d[:2])); days.append(day)
    parts.append(transform(decode_day(f, day, 1e-5, 5), day))
new = pd.concat([p for p in parts if p is not None]).set_index("timestamp")
e = ex[ex.index.normalize().isin([pd.Timestamp(d, tz="UTC") for d in days if d.weekday() != 5])]
print("gun sayisi", len(days), "yeni satir", len(new), "mevcut satir (ayni gunler)", len(e))
j = new.join(e, how="outer", lsuffix="_n", rsuffix="_e")
only_n, only_e = j.open_e.isna().sum(), j.open_n.isna().sum()
both = j.dropna()
exact = np.ones(len(both), bool); tol = np.ones(len(both), bool)
for c in ["open", "high", "low", "close"]:
    exact &= (both[c+"_n"] == both[c+"_e"]).values; tol &= ((both[c+"_n"] - both[c+"_e"]).abs() <= 1e-9).values
print("sadece yeni", only_n, "sadece mevcut", only_e, "ortak", len(both), "birebir esit", exact.sum(), "1e-9 icinde", tol.sum())
print("ESLESME ORANI (1e-9):", tol.sum() / len(j))
