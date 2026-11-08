"""Backtest işlemlerini okunabilir CSV'ye çevirir: out/islemler_{NQ,ES}.csv

Backtest, roll sıçramalarını temizlemek için oran-ayarlı (ratio-adjusted) sürekli seride yapılır.
Grafikte kontrol edilebilsin diye CSV'ye o günkü kontratın gerçek fiyatları da yazılır:
gerçek fiyat = ayarlı fiyat / adj_factor (o günün 09:30 barı).
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "faz0"))
from dreyko_data import load_is  # noqa: E402

KURULUM = {"H1-A": "FPFVG retest (pencere A)", "H1-B": "FPFVG retest (pencere B)",
           "H2": "Sweep + IFVG", "H2b": "Sweep + Turtle Soup + CISD"}
HEDEF = {"L": "açılış öncesi range karşı ucu", "R": "2R"}


def main():
    for sym in ("NQ", "ES"):
        tr = pd.read_parquet(HERE / f"out/trades_{sym}.parquet")
        df = load_is(sym, ["adj_factor"])
        mod = df.index.hour * 60 + df.index.minute
        adj = df[mod == 9 * 60 + 30].groupby("session_date").adj_factor.first()
        f = tr.date.map(adj)
        assert f.notna().all()
        out = pd.DataFrame({
            "tarih": tr.date.dt.strftime("%Y-%m-%d"),
            "giris_saati_NY": [f"{m // 60:02d}:{m % 60:02d}" for m in tr.entry_mod],
            "kurulum": tr.hyp.map(KURULUM), "kod": tr.hyp,
            "hedef_turu": tr.target.map(HEDEF),
            "yon": tr.d.map({1: "long", -1: "short"}),
            "giris": (tr.entry / f).round(2), "stop": (tr.stop / f).round(2),
            "hedef": (tr.tgt / f).round(2), "cikis": (tr.exit / f).round(2),
            "cikis_nedeni": tr.why,
            "risk_puan": tr.risk_pts.round(2), "net_puan": tr.net_pts.round(2),
            "R": tr.R.round(3), "net_usd_1kontrat": tr.usd.round(2),
            "smt": tr.smt.astype("Int64"), "makro_0950_1010": tr.makro.astype(int),
        })
        out.to_csv(HERE / f"out/islemler_{sym}.csv", index=False)
        print(sym, len(out))


if __name__ == "__main__":
    main()
