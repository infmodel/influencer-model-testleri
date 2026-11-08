"""Dukascopy ham yıllık parquet -> data/ şemasında işlenmiş 1dk + günlük özet.

Mantık, mevcut 4 paritenin işlenmiş dosyalarını üreten pipeline'ın (process_bars_and_daily) BİREBİR kopyasıdır; yalnız giriş/çıkış klasörü parametre.
Doğrulama: `--dogrula eurusd` mevcut EURUSD işlenmiş dosyasını yeniden üretip eşitliği kontrol eder
(yalnız yapısal eşitlik; fiyat/getiri/performans yazdırılmaz).

Kullanım:
  python islenmis.py RAW_DIR OUT_DIR PAIR [PAIR ...]
  python islenmis.py --dogrula RAW_DIR REF_DIR eurusd
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]


def load_raw_pair(raw_dir: Path, pair: str) -> pd.DataFrame:
    dfs = []
    for y in YEARS:
        pq = raw_dir / f"{pair}_{y}.parquet"
        if not pq.exists():
            raise FileNotFoundError(pq)
        dfs.append(pd.read_parquet(pq))
    df = pd.concat(dfs, ignore_index=True)
    df["ts_event"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("ts_event").drop_duplicates(subset=["ts_event"]).reset_index(drop=True)
    return df[["ts_event", "open", "high", "low", "close"]].copy()


def process_bars_and_daily(df: pd.DataFrame):
    df["ts_london"] = df["ts_event"].dt.tz_convert("Europe/London")
    df["london_date"] = df["ts_london"].dt.date
    df["london_hour"] = df["ts_london"].dt.hour
    df["london_minute"] = df["ts_london"].dt.minute
    df["london_time_min"] = df["london_hour"] * 60 + df["london_minute"]
    df["london_dow"] = df["ts_london"].dt.dayofweek

    df["ts_ny"] = df["ts_event"].dt.tz_convert("America/New_York")
    df["ny_date"] = df["ts_ny"].dt.date
    df["ny_hour"] = df["ts_ny"].dt.hour
    df["ny_minute"] = df["ts_ny"].dt.minute
    df["ny_dow"] = df["ts_ny"].dt.dayofweek

    df["ts_tokyo"] = df["ts_event"].dt.tz_convert("Asia/Tokyo")
    df["tokyo_hour"] = df["ts_tokyo"].dt.hour
    df["tokyo_minute"] = df["ts_tokyo"].dt.minute

    mask_weekend = (df["ny_dow"] == 5) | \
                   ((df["ny_dow"] == 6) & (df["ny_hour"] < 17)) | \
                   ((df["ny_dow"] == 4) & (df["ny_hour"] >= 17))
    df = df[~mask_weekend].copy().reset_index(drop=True)

    df["fx_date"] = df["ny_date"]
    mask_after_17 = df["ny_hour"] >= 17
    df.loc[mask_after_17, "fx_date"] = df.loc[mask_after_17, "ny_date"] + pd.Timedelta(days=1)
    df["trading_date"] = df["fx_date"]

    df["prev_close"] = df["close"].shift(1)
    df["ret_1m"] = df["close"] - df["prev_close"]
    df.loc[df.index[0], "ret_1m"] = df.loc[df.index[0], "close"] - df.loc[df.index[0], "open"]
    df.drop(columns=["prev_close"], inplace=True)

    daily_df = df.groupby("trading_date").agg(
        open_d=("open", "first"), high_d=("high", "max"), low_d=("low", "min"),
        close_d=("close", "last"), bar_count=("close", "count")).reset_index()
    daily_df["prev_close_d"] = daily_df["close_d"].shift(1)
    tr_hl = daily_df["high_d"] - daily_df["low_d"]
    tr_h_pc = (daily_df["high_d"] - daily_df["prev_close_d"]).abs()
    tr_l_pc = (daily_df["low_d"] - daily_df["prev_close_d"]).abs()
    tr_standard = np.maximum(tr_hl, np.maximum(tr_h_pc, tr_l_pc))
    daily_df["TR_d"] = np.where(daily_df["prev_close_d"].isna(), tr_hl, tr_standard)
    daily_df["ATR_14_d1"] = daily_df["TR_d"].rolling(14).mean().shift(1)
    daily_df["PDH"] = daily_df["high_d"].shift(1)
    daily_df["PDL"] = daily_df["low_d"].shift(1)
    daily_df["PDC"] = daily_df["close_d"].shift(1)
    daily_df["PDO_d1"] = daily_df["open_d"].shift(1)
    daily_df["PD_Range"] = daily_df["PDH"] - daily_df["PDL"]

    def calc_percentile_rank(window):
        if len(window) < 15 or np.isnan(window.iloc[-1]):
            return np.nan
        val = window.iloc[-1]
        valid = window.dropna()
        if len(valid) == 0:
            return np.nan
        return float((valid < val).mean() * 100.0)

    daily_df["ATR_Regime_Pct_60d"] = daily_df["ATR_14_d1"].rolling(60).apply(calc_percentile_rank, raw=False)
    daily_df["year"] = pd.to_datetime(daily_df["trading_date"]).dt.year
    daily_df["month"] = pd.to_datetime(daily_df["trading_date"]).dt.month
    daily_df["is_oos_2026"] = daily_df["year"] == 2026
    daily_df.drop(columns=["prev_close_d"], inplace=True)

    merge_cols = ["trading_date", "PDH", "PDL", "PDC", "PDO_d1", "PD_Range", "ATR_14_d1",
                  "ATR_Regime_Pct_60d", "is_oos_2026", "month", "year"]
    df = df.merge(daily_df[merge_cols], on="trading_date", how="left")
    return df, daily_df


def summary(sym, df, daily_df, proc_path, daily_path):
    return {"symbol": sym, "bars_count": len(df), "days_count": len(daily_df),
            "min_date": str(df["ts_event"].min()), "max_date": str(df["ts_event"].max()),
            "is_days": int((~daily_df["is_oos_2026"]).sum()), "oos_days": int(daily_df["is_oos_2026"].sum()),
            "mean_atr": float(daily_df.loc[~daily_df["is_oos_2026"], "ATR_14_d1"].mean()),
            "mean_atr_kapsam": "yalnız IS (2020-2025)",
            "proc_file": str(proc_path), "daily_file": str(daily_path)}


def main():
    if sys.argv[1] == "--dogrula":
        raw_dir, ref_dir, pair = Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
        df, daily = process_bars_and_daily(load_raw_pair(raw_dir, pair))
        ref = pd.read_parquet(ref_dir / f"fx_dukas_{pair}_1m_processed.parquet")
        ref_d = pd.read_parquet(ref_dir / f"fx_dukas_{pair}_daily_summary.parquet")
        pd.testing.assert_frame_equal(df, ref, check_dtype=True)
        pd.testing.assert_frame_equal(daily, ref_d, check_dtype=True)
        print(f"DOGRULAMA OK {pair}: 1dk {len(df)} satir, {df.shape[1]} kolon; gunluk {len(daily)} satir — birebir esit")
        return
    raw_dir, out_dir, pairs = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]
    out_dir.mkdir(parents=True, exist_ok=True)
    res = {}
    for pair in pairs:
        proc_path = out_dir / f"fx_dukas_{pair}_1m_processed.parquet"
        daily_path = out_dir / f"fx_dukas_{pair}_daily_summary.parquet"
        assert not proc_path.exists() and not daily_path.exists(), f"üstüne yazma yok: {proc_path}"
        df, daily = process_bars_and_daily(load_raw_pair(raw_dir, pair))
        df.to_parquet(proc_path, engine="pyarrow", compression="zstd")
        daily.to_parquet(daily_path, engine="pyarrow", compression="zstd")
        res[pair] = summary(pair, df, daily, proc_path, daily_path)
        print(pair, len(df), "bar", len(daily), "gun", flush=True)
    (out_dir / "ozet_yeni_pariteler.json").write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
