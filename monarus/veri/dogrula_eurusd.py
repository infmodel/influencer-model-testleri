"""Argumanlar: dogrulama_klasoru mevcut_parquet. EURUSD bi5'lerini mevcut ham dosyayla dakika dakika karsilastirir."""
import sys, glob, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
from decode import decode_day
folder, pq = sys.argv[1], sys.argv[2]
ex = pd.read_parquet(pq).set_index("timestamp")
for f in sorted(glob.glob(folder + "/EURUSD/*/*/*.bi5")):
    y, m, d = f.split("/")[-3:]; d = d[:2]; day = dt.date(int(y), int(m), int(d))
    n = decode_day(f, day, 1e-5)
    e = ex[(ex.index.date == day)]
    if n is None: print(day, "bi5 bos; mevcut satir:", len(e)); continue
    n = n.set_index("timestamp")
    j = n.join(e, how="outer", lsuffix="_n", rsuffix="_e")
    both = j.dropna(subset=["open_n", "open_e"])
    ok = np.ones(len(both), bool)
    for c in ["open", "high", "low", "close"]:
        ok &= (both[c+"_n"] - both[c+"_e"]).abs() <= 1e-9
    flat = ((n.open == n.high) & (n.high == n.low) & (n.low == n.close)).sum()
    print(day, day.strftime("%a"), "yeni", len(n), "mevcut", len(e), "ortak", len(both), "esles", int(ok.sum()),
          "sadece_yeni", int(j.open_e.isna().sum()), "sadece_mevcut", int(j.open_n.isna().sum()), "yeni_duz", int(flat),
          "ilk/son", n.index.min().strftime("%H:%M"), n.index.max().strftime("%H:%M"))
