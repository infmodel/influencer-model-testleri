"""Backtest işlemlerini okunabilir CSV'lere çevirir: out/islemler/islemler_<model>.csv

Fiyatlar grafikte kontrol edilebilsin diye gerçek fiyattır:
- Spot FX (Dukascopy BID): ayar yok, aynen.
- XAUUSD (CME GC): backtest fark-ayarlı seride; gerçek = ayarlı - (open_adj - open) (giriş dakikasındaki fark).
- NQ: backtest oran-ayarlı seride; gerçek = ayarlı / adj_factor (giriş dakikası).
Çıkış fiyatı = giriş + yön x R x risk (ayarlı birimde), aynı dönüşümle.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "adim0"))
import common as C  # noqa: E402
import m_mc  # noqa: E402

ACIKLAMA = {
    "MA-T": "Günlük bias + %50 + 1S konfirme", "ME-1": "Günlük bias + 4S CRT", "ME-1n": "4S CRT (bias'sız, kontrol)",
    "ME-2": "Haftalık bias + günlük CRT", "MF-1": "Haftalık bias + PDH/PDL sweep + 15dk CHoCH (kararsız hafta pas)",
    "MF-1k": "MF, kararsız haftada devam", "MF-n": "PDH/PDL sweep + CHoCH (bias'sız, kontrol)",
    "MF-1-atr": "MF-1, sweep sınırı 0,4 ATR", "MB-v": "15dk marubozu 1:1, SMA21 + yapı", "MB-s": "15dk marubozu 1:1, WMA26→SMA5 + yapı",
    "MB-h0": "15dk marubozu 1:1 (filtresiz, kontrol)", "MC-A-0.5": "NQ sweep + CISD, stop ≤%0,5",
    "MC-A-1.0": "NQ sweep + CISD, stop ≤%1", "MC-B-0.5": "NQ sweep + engulf limit, stop ≤%0,5",
    "MC-B-1.0": "NQ sweep + engulf limit, stop ≤%1",
}


def describe(model: str) -> str:
    base = model.replace("-BE", "")
    if base.startswith("MD-"):
        parts = base.split("-")
        poi = {"4S": "4S FVG", "1G": "1G FVG", "n0": "POI'siz"}[parts[1]]
        ent = {"a": "MSB kapanışında market", "b": "30dk FVG limiti"}[parts[2]]
        return f"MD: {poi} + 30dk sweep + MSB, {ent}" + (", 1,8R filtresiz" if base.endswith("n1") else ", min 1,8R")
    return ACIKLAMA.get(base, base) + (" + BE" if model.endswith("-BE") else "")


def converters():
    """enstrüman -> (t dizisi, giriş indeksine göre dönüşüm fonksiyonu)."""
    conv = {}
    for name in C.FX6:
        conv[name] = lambda px, i: px
    gc_adj = pd.read_parquet(C.md.GC_IS, columns=["open_adj"]).sort_index()
    gc_raw = pd.read_parquet(C.md.GC_IS, columns=["open"]).sort_index()
    off = (gc_adj["open_adj"] - gc_raw["open"]).to_numpy()
    conv["XAUUSD"] = lambda px, i, off=off: px - off[i]
    sys.path.insert(0, str(next((C.HERE.parents[1] / d / "faz0" for d in ("Dreyko", "dreyko")
                                 if (C.HERE.parents[1] / d / "faz0").exists()))))
    from dreyko_data import load_is
    nq = load_is("NQ", ["adj_factor", "ts_utc"])
    s = pd.Series(nq["adj_factor"].to_numpy(), index=pd.DatetimeIndex(nq["ts_utc"]).tz_convert("UTC")
                  if pd.DatetimeIndex(nq["ts_utc"]).tz else pd.DatetimeIndex(nq["ts_utc"]).tz_localize("UTC"))
    s = s[~s.index.duplicated()].sort_index()
    inst = m_mc.load_nq()
    fac = s.reindex(pd.DatetimeIndex(inst.t).tz_localize("UTC")).to_numpy()
    assert np.isfinite(fac).all()
    conv["NQ"] = lambda px, i, fac=fac: px / fac[i]
    return conv


def main():
    tr = pd.read_parquet(HERE / "out/trades.parquet")
    conv = converters()
    out_dir = HERE / "out/islemler"
    out_dir.mkdir(exist_ok=True)
    tr["exit_px"] = tr.entry + tr.d * tr.R * tr.risk_px
    rows = []
    for r in tr.itertuples():
        f = conv[r.inst]
        rows.append({
            "model": r.model, "aciklama": describe(r.model), "enstruman": r.inst, "gun_siniri": r.boundary,
            "giris_utc": r.t_entry.strftime("%Y-%m-%d %H:%M"),
            "giris_tr": (r.t_entry + pd.Timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
            "yon": "long" if r.d == 1 else "short",
            "giris": f(r.entry, r.i0), "stop": f(r.stop, r.i0), "hedef": f(r.tp, r.i0),
            "cikis_utc": r.t_exit.strftime("%Y-%m-%d %H:%M"), "cikis": f(r.exit_px, r.i0),
            "sonuc": "TP" if r.hit == 1 else ("stop" if r.R <= -0.999 else "süre sonu"),
            "RR": round(r.rr, 3), "R": round(r.R, 4),
            "maliyet_R": round(r.cost_R, 4), "R_net": round(r.R_net, 4)})
    df = pd.DataFrame(rows)
    nd = {"NQ": 2, "XAUUSD": 2, "USDJPY": 3}
    for c in ("giris", "stop", "hedef", "cikis"):
        df[c] = [round(v, nd.get(i, 5)) for v, i in zip(df[c], df["enstruman"])]
    df.insert(df.columns.get_loc("RR"), "risk_fiyat", [round(abs(a - b), nd.get(i, 5)) for a, b, i in
                                                      zip(df["giris"], df["stop"], df["enstruman"])])
    df.insert(df.columns.get_loc("RR"), "risk_pip", [round(abs(a - b) / C.PIP[i], 1) if i in C.FX6 else np.nan
                                                    for a, b, i in zip(df["giris"], df["stop"], df["enstruman"])])
    for m, g in df.groupby("model"):
        g.to_csv(out_dir / f"islemler_{m}.csv", index=False)
    print(len(df), "işlem,", df.model.nunique(), "dosya")


if __name__ == "__main__":
    main()
