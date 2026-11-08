"""Faz 0 veri kontrolleri: Dreyko modeli için NQ/ES 1dk IS verisi (2020-2025).

Sadece veri bütünlüğü ve pencere kapsamı kontrol edilir. Sinyal, getiri veya
performans hesabı YOKTUR. 2026 OOS dosyalarına dokunulmaz.

Kullanım: python3 faz0_checks.py  -> faz0/faz0_results.json + konsol özeti
"""
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(os.environ.get("TRADE_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))
FILES = {
    "NQ": DATA / "NQ_Nasdaq/processed/nq_1m_continuous_2020_2025.parquet",
    "ES": DATA / "ES_SP500/processed/es_1m_continuous_2020_2025.parquet",
}
CAL = DATA / "FX_Currencies/macro_calendars/macro_calendar_2020_2026.parquet"
OUT = Path(__file__).parent / "faz0_results.json"
IS_END = pd.Timestamp("2026-01-01")

# Dreyko modelinin kullandığı pencereler (NY duvar saati, [başlangıç, bitiş) dakika)
WINDOWS = {
    "asia_2000_0000": ("20:00", "00:00"),   # önceki takvim günü akşamı (session_date içinde)
    "premarket_0800_0930": ("08:00", "09:30"),
    "open_0930_1000": ("09:30", "10:00"),
    "macro_0950_1010": ("09:50", "10:10"),
    "am_0930_1210": ("09:30", "12:10"),
}


def minute_of_day(idx: pd.DatetimeIndex) -> np.ndarray:
    return idx.hour * 60 + idx.minute


def hm(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def window_mask(mod: np.ndarray, start: str, end: str) -> np.ndarray:
    """[start, end) dakika maskesi; end <= start ise gece yarısını geçer."""
    a, b = hm(start), hm(end)
    if b <= a:
        return (mod >= a) | (mod < b)
    return (mod >= a) & (mod < b)


def expected_minutes(start: str, end: str) -> int:
    a, b = hm(start), hm(end)
    return (b - a) if b > a else (1440 - a + b)


def load(sym: str) -> pd.DataFrame:
    df = pd.read_parquet(FILES[sym])
    assert df.index.max() < IS_END, "IS dosyasında 2026 verisi var"
    return df


def basic_integrity(df: pd.DataFrame) -> dict:
    idx = df.index
    unadj = df[["open_unadj", "high_unadj", "low_unadj", "close_unadj"]].to_numpy()
    off_tick = np.abs(np.round(unadj / 0.25) * 0.25 - unadj) > 1e-9
    return {
        "rows": int(len(df)),
        "start": str(idx.min()),
        "end": str(idx.max()),
        "dup_ts": int(idx.duplicated().sum()),
        "monotonic": bool(idx.is_monotonic_increasing),
        "nan_ohlc": int(df[["open", "high", "low", "close"]].isna().sum().sum()),
        "high_lt_low": int((df["high"] < df["low"]).sum()),
        "ohlc_outside_hl": int(((df["open"] > df["high"] + 1e-9) | (df["open"] < df["low"] - 1e-9)
                                | (df["close"] > df["high"] + 1e-9) | (df["close"] < df["low"] - 1e-9)).sum()),
        "zero_volume": int((df["volume"] == 0).sum()),
        "unadj_off_tick_0.25": int(off_tick.any(axis=1).sum()),
    }


def utc_offset_check(df: pd.DataFrame) -> dict:
    """datetime_ny - ts_utc farkı yalnızca -4h / -5h olmalı; DST geçişleri ABD takvimine uymalı."""
    ny_from_utc = df["ts_utc"].dt.tz_convert("America/New_York").dt.tz_localize(None)
    mismatch = int((ny_from_utc.to_numpy() != df.index.to_numpy()).sum())
    off = (df.index.to_series().reset_index(drop=True) - df["ts_utc"].dt.tz_localize(None).reset_index(drop=True))
    offs = sorted({int(x) for x in (off.dt.total_seconds() / 3600).unique()})
    return {"ny_vs_utc_mismatch_rows": mismatch, "offsets_hours": offs}


def session_semantics(df: pd.DataFrame) -> dict:
    """is_rth sınırları ve session_date (18:00 ET başlangıç) tutarlılığı."""
    mod = minute_of_day(df.index)
    rth = df["is_rth"].to_numpy()
    rth_mod = mod[rth]
    # session_date: 18:00 ve sonrası -> ertesi gün
    cal_date = df.index.normalize()
    exp_sess = np.where(mod >= 18 * 60, cal_date + pd.Timedelta(days=1), cal_date)
    sess_mismatch = int((df["session_date"].to_numpy() != exp_sess.astype("datetime64[ns]")).sum())
    return {
        "rth_first_minute": f"{rth_mod.min() // 60:02d}:{rth_mod.min() % 60:02d}",
        "rth_last_minute": f"{rth_mod.max() // 60:02d}:{rth_mod.max() % 60:02d}",
        "session_date_mismatch_rows": sess_mismatch,
        "rth_and_eth_both_true": int((df["is_rth"] & df["is_eth"]).sum()),
        "neither_rth_nor_eth": int((~df["is_rth"] & ~df["is_eth"]).sum()),
    }


def bar_label_semantics(df: pd.DataFrame) -> dict:
    """Bar etiketi açılış mı kapanış mı? 09:30 açılış hacmi 09:30 etiketli barda mı, 09:31'de mi?"""
    mod = minute_of_day(df.index)
    vol = pd.Series(df["volume"].to_numpy(), index=mod).groupby(level=0).median()
    pick = {f"{m // 60:02d}:{m % 60:02d}": float(vol.get(m, np.nan)) for m in
            [hm("08:29"), hm("08:30"), hm("08:31"), hm("09:28"), hm("09:29"), hm("09:30"), hm("09:31"), hm("15:59"), hm("16:00")]}
    return {"median_volume_by_minute": pick}


def window_coverage(df: pd.DataFrame) -> dict:
    """Her işlem günü (RTH'si olan) için pencere içi eksik dakika istatistikleri."""
    mod = minute_of_day(df.index)
    sess = df["session_date"].to_numpy()
    rth_days = pd.Index(np.unique(sess[df["is_rth"].to_numpy()]))
    res = {"n_rth_sessions": int(len(rth_days))}
    for name, (a, b) in WINDOWS.items():
        m = window_mask(mod, a, b)
        cnt = pd.Series(1, index=sess[m]).groupby(level=0).sum().reindex(rth_days, fill_value=0)
        exp = expected_minutes(a, b)
        miss = exp - cnt
        res[name] = {
            "expected_min": exp,
            "days_full": int((miss == 0).sum()),
            "days_missing_any": int((miss > 0).sum()),
            "days_empty": int((cnt == 0).sum()),
            "median_missing": float(miss.median()),
            "p95_missing": float(miss.quantile(0.95)),
            "max_missing": int(miss.max()),
            "worst_days": [str(d.date()) for d in miss.sort_values(ascending=False).index[:5]],
        }
    return res


def consecutive_triplets(df: pd.DataFrame, start: str, end: str) -> dict:
    """FVG 3 ardışık bar ister. Pencerede ardışık-dakika (gap'siz) 3'lü oranı."""
    mod = minute_of_day(df.index)
    m = window_mask(mod, start, end)
    t = df.index[m].to_series()
    d1 = t.diff().dt.total_seconds().eq(60)
    ok = d1 & d1.shift(1, fill_value=False)
    return {"window": f"{start}-{end}", "bars": int(m.sum()), "triplets_contiguous_share": float(ok.iloc[2:].mean())}


def early_close_and_holidays(df: pd.DataFrame) -> dict:
    rth = df[df["is_rth"]]
    last = rth.groupby("session_date").apply(lambda x: x.index.max().hour * 60 + x.index.max().minute)
    first = rth.groupby("session_date").apply(lambda x: x.index.min().hour * 60 + x.index.min().minute)
    early = last[last < hm("15:59")]
    late_open = first[first > hm("09:30")]
    bdays = pd.bdate_range("2020-01-02", "2025-12-31")
    no_rth = bdays.difference(pd.DatetimeIndex(last.index))
    return {
        "early_close_days": [f"{d.date()} ({v // 60:02d}:{v % 60:02d})" for d, v in early.items()],
        "late_rth_open_days": [f"{d.date()} ({v // 60:02d}:{v % 60:02d})" for d, v in late_open.items()],
        "weekdays_without_rth": [str(d.date()) for d in no_rth],
    }


def roll_info(df: pd.DataFrame) -> dict:
    r = df[df["roll_flag"]]
    rows = []
    for ts, row in r.iterrows():
        mod = ts.hour * 60 + ts.minute
        inwin = [n for n, (a, b) in WINDOWS.items() if window_mask(np.array([mod]), a, b)[0]]
        rows.append({"ts_ny": str(ts), "weekday": ts.day_name(), "symbol": str(row["symbol"]),
                     "in_windows": inwin})
    return {"n_rolls": len(rows), "rolls": rows}


def nq_es_alignment(nq: pd.DataFrame, es: pd.DataFrame) -> dict:
    out = {}
    for name in ["premarket_0800_0930", "am_0930_1210", "asia_2000_0000"]:
        a, b = WINDOWS[name]
        i1 = nq.index[window_mask(minute_of_day(nq.index), a, b)]
        i2 = es.index[window_mask(minute_of_day(es.index), a, b)]
        inter = i1.intersection(i2)
        out[name] = {"nq_bars": int(len(i1)), "es_bars": int(len(i2)), "both": int(len(inter)),
                     "nq_only": int(len(i1.difference(i2))), "es_only": int(len(i2.difference(i1)))}
    return out


def calendar_check(df: pd.DataFrame) -> dict:
    """CPI/NFP 08:30 ET: takvim saatinde gerçekten range/hacim sıçraması var mı (IS yılları)."""
    cal = pd.read_parquet(CAL)
    cal = cal[(~cal["is_oos_2026"]) & cal["event_type"].isin(["CPI", "NFP"])]
    ts_ny = cal["ts_release"].dt.tz_convert("America/New_York").dt.tz_localize(None)
    rng = (df["high"] - df["low"]) / df["close"]
    mod = minute_of_day(df.index)
    base = rng[mod == hm("08:30")]
    event_vals, vol_ratio, missing = [], [], 0
    vol = df["volume"].astype(float)
    for t in ts_ny:
        if t not in df.index:
            missing += 1
            continue
        event_vals.append(rng.loc[t])
        prev = vol.loc[t - pd.Timedelta(minutes=10): t - pd.Timedelta(minutes=1)]
        if len(prev) and prev.median() > 0:
            vol_ratio.append(vol.loc[t] / prev.median())
    ev = pd.Series(event_vals)
    non_event = base.drop(index=[t for t in ts_ny if t in base.index], errors="ignore")
    return {
        "n_events_IS": int(len(ts_ny)),
        "missing_bar_at_release": missing,
        "median_range_0830_event_pct": float(ev.median() * 100),
        "median_range_0830_nonevent_pct": float(non_event.median() * 100),
        "median_vol_ratio_event_vs_prev10": float(np.median(vol_ratio)),
        "share_events_vol_ratio_gt3": float(np.mean(np.array(vol_ratio) > 3)),
        "release_minutes": sorted({f"{t.hour:02d}:{t.minute:02d}" for t in ts_ny}),
    }


def main():
    res = {}
    dfs = {s: load(s) for s in FILES}
    for s, df in dfs.items():
        print(f"== {s}")
        res[s] = {
            "integrity": basic_integrity(df),
            "utc": utc_offset_check(df),
            "session": session_semantics(df),
            "bar_label": bar_label_semantics(df),
            "coverage": window_coverage(df),
            "triplets": [consecutive_triplets(df, "20:00", "00:00"), consecutive_triplets(df, "08:00", "09:30"),
                         consecutive_triplets(df, "09:30", "12:10")],
            "calendar_rth": early_close_and_holidays(df),
            "rolls": roll_info(df),
            "macro_calendar": calendar_check(df),
        }
        print(json.dumps({k: v for k, v in res[s].items() if k not in ("rolls", "calendar_rth")}, indent=1, default=str)[:4000])
    res["NQ_ES_alignment"] = nq_es_alignment(dfs["NQ"], dfs["ES"])
    print(json.dumps(res["NQ_ES_alignment"], indent=1))
    OUT.write_text(json.dumps(res, indent=1, default=str))
    print("yazıldı:", OUT)


if __name__ == "__main__":
    main()
