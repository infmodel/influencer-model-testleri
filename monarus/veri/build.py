"""Arguman: SEMBOL point ondalik indirme_klasoru cikti_klasoru. Yil basina parquet yazar (atomik)."""
import sys, os, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from donustur import decode_day, transform
sym, point, nd, src, out = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
os.makedirs(out, exist_ok=True)
rep = {"eksik": [], "bos_veya_404": []}
YILLAR = [int(y) for y in os.environ.get("YILLAR", "2020,2021,2022,2023,2024,2025").split(",")]
for year in YILLAR:
    parts = []
    d = dt.date(year, 1, 1)
    while d.year == year:
        if d.weekday() != 5:
            p = f"{src}/{sym}/{d.year}/{d.month:02d}/{d.day:02d}.bi5"
            if os.path.exists(p):
                df = decode_day(p, d, point, nd)
                if df is None: rep["bos_veya_404"].append(str(d))
                else:
                    t = transform(df, d)
                    if t is not None and len(t): parts.append(t)
            elif os.path.exists(p + ".404"): rep["bos_veya_404"].append(str(d))
            else: rep["eksik"].append(str(d))
        d += dt.timedelta(1)
    df = pd.concat(parts).sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)
    fn = f"{out}/{sym.lower()}_{year}.parquet"
    df.to_parquet(fn + ".tmp", index=False); os.replace(fn + ".tmp", fn)
    print(sym, year, len(df))
json.dump(rep, open(f"{out}/../{sym.lower()}_build_rapor{os.environ.get('RAPOR_EK', '')}.json", "w"), indent=1)
print(rep)
