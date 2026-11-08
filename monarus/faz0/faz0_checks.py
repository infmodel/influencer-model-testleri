"""Faz 0 veri kontrolleri: Monarus modelleri (MA–MF) için FX/altın IS verisi (2020-2025).

Yalnızca veri bütünlüğü, zaman semantiği, gün/blok yapısı, roll ve vekil (spot<->vadeli)
uygunluğu kontrol edilir. Sinyal sonucu, getiri-sonrası etiket veya performans hesabı YOKTUR.
2026 OOS verisi yüklenmez (monarus_data._guard).

Kullanım: python3 faz0_checks.py -> faz0_results.json + konsol özeti
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import monarus_data as md

OUT = Path(__file__).parent / "faz0_results.json"
CAL = md.DATA / "FX_Currencies/macro_calendars/macro_calendar_2020_2026.parquet"
INSTR = ["EURUSD", "GBPUSD", "USDCAD", "USDCHF", "AUDUSD", "USDJPY", "AUDUSD_FUT", "USDJPY_FUT", "XAUUSD", "6E", "6B"]
EPS = 1e-9


def integrity(df: pd.DataFrame) -> dict:
    idx = df.index
    o, h, l, c = (df[k].to_numpy() for k in md.OHLC)
    r = {
        "rows": int(len(df)), "start": str(idx.min()), "end": str(idx.max()),
        "dup_ts": int(idx.duplicated().sum()), "monotonic": bool(idx.is_monotonic_increasing),
        "nan_ohlc": int(df[md.OHLC].isna().sum().sum()),
        "nonpos": int((df[md.OHLC] <= 0).sum().sum()),
        "high_lt_low": int((h < l - EPS).sum()),
        "oc_outside_hl": int(((o > h + EPS) | (o < l - EPS) | (c > h + EPS) | (c < l - EPS)).sum()),
    }
    if df["volume"].notna().any():
        r["zero_volume"] = int((df["volume"] == 0).sum())
    return r


def release_spike(df: pd.DataFrame, pip: float) -> dict:
    """Bar etiketi açılış mı? Haber dakikası etiketli barın range'i bir önceki ve sonraki
    bara göre (medyan, pip). Olay sonrası takvim kolonları KULLANILMAZ; yalnız ts_release."""
    cal = pd.read_parquet(CAL, columns=["event_type", "ts_release", "is_oos_2026"])
    cal = cal[~cal["is_oos_2026"]]
    rng = (df["high"] - df["low"]) / pip
    out = {}
    for ev in ["NFP", "CPI", "FOMC"]:
        t = pd.DatetimeIndex(cal.loc[cal.event_type == ev, "ts_release"])
        row = {}
        for lag in [-1, 0, 1]:
            v = rng.reindex(t + pd.Timedelta(minutes=lag)).dropna()
            row[f"m{lag:+d}"] = round(float(v.median()), 2) if len(v) else None
        row["n"] = int(len(t))
        out[ev] = row
    return out


def day_structure(df: pd.DataFrame, boundary: str) -> dict:
    d = md.daily(df, boundary)
    med = float(d["n_min"].median())
    short = d[d["n_min"] < 0.5 * med]
    r = {
        "days": int(len(d)), "median_minutes": med,
        "weekday_counts": {int(k): int(v) for k, v in d.index.dayofweek.value_counts().sort_index().items()},
        "short_days_lt50pct": int(len(short)),
        "short_days_list": [str(x.date()) for x in short.index][:40],
        "days_per_year": {int(k): int(v) for k, v in d.groupby(d.index.year).size().items()},
    }
    if boundary == "tr":
        loc = df.index.tz_convert(md.TR)
        r["saturday_stub_minutes"] = int((loc.dayofweek == 5).sum())
        r["sunday_tr_minutes"] = int((loc.dayofweek == 6).sum())
    w = md.weekly(df, boundary)
    r["weeks"] = int(len(w))
    r["short_weeks_lt3days"] = int((md.daily(df, boundary).groupby(
        lambda x: x - pd.Timedelta(days=x.dayofweek)).size() < 3).sum())
    return r


def intraday_coverage(df: pd.DataFrame, minutes: int) -> dict:
    """Monarus işlem penceresi (TR 08:00–18:00 = 05:00–15:00 UTC) içindeki barların doluluk oranı."""
    b = md.intraday(df, minutes)
    hr = b.index.hour
    win = b[(hr >= 5) & (hr < 15)]
    return {
        "bars_in_window": int(len(win)),
        "full_pct": round(float((win["n_min"] == minutes).mean() * 100), 2),
        "ge90pct_pct": round(float((win["n_min"] >= 0.9 * minutes).mean() * 100), 2),
    }


def roll_check(name: str) -> dict:
    """Roll barında 1dk açılış boşluğu: ayarlı vs ayarsız (pip). Ayarlı seri sıçramayı gidermeli."""
    adj = md.load(name, adjusted=True) if name != "XAUUSD" else md.load_gc()
    if name == "XAUUSD":
        raw = pd.read_parquet(md.GC_IS, columns=md.OHLC)
    else:
        raw = md.load(name, adjusted=False)
    pip = md.PIP[name]
    rb = adj.index[adj["roll_flag"].to_numpy()]
    res = {"n_roll_bars": int(len(rb)), "roll_dates": [str(x.date()) for x in rb]}
    for lab, d in [("adj", adj), ("unadj", raw)]:
        prev_close = d["close"].shift(1)
        gap = ((d["open"] - prev_close).abs() / pip).reindex(rb)
        res[f"median_gap_pip_{lab}"] = round(float(gap.median()), 2)
        res[f"max_gap_pip_{lab}"] = round(float(gap.max()), 2)
    nonroll = ((adj["open"] - adj["close"].shift(1)).abs() / pip)[~adj["roll_flag"]]
    res["median_gap_pip_nonroll"] = round(float(nonroll.median()), 3)
    res["p999_gap_pip_nonroll"] = round(float(nonroll.quantile(0.999)), 2)
    return res


def ma_state(d: pd.DataFrame) -> pd.Series:
    """Günlük durum sınıfı (yalnız D ve D-1 OHLC; sonuç/etiket yok). model_taslak MA tablosu."""
    H1, L1 = d["high"].shift(1), d["low"].shift(1)
    H, L, C = d["high"], d["low"], d["close"]
    s = pd.Series("na", index=d.index)
    s[(H <= H1) & (L >= L1)] = "inside"
    s[(H > H1) & (L < L1) & (C <= H1) & (C >= L1)] = "kararsiz"
    s[C > H1] = "flow_long"
    s[C < L1] = "flow_short"
    s[(H > H1) & (C <= H1) & (L >= L1)] = "crt_short"
    s[(L < L1) & (C >= L1) & (H <= H1)] = "crt_long"
    s[H1.isna()] = "na"
    return s


def proxy_check(spot: str, fut: str, boundary: str = "ny17") -> dict:
    """Vadeli, spotun vekili olarak ne kadar uygun? (6E~EURUSD, 6B~GBPUSD)."""
    a, b = md.load(spot), md.load(fut, adjusted=True)
    da, db = md.daily(a, boundary), md.daily(b, boundary)
    j = da.index.intersection(db.index)
    ra = np.log(da.loc[j, "close"]).diff()
    rb = np.log(db.loc[j, "close"]).diff()
    ok = ~db.loc[j, "has_roll"].to_numpy()
    sa, sb = ma_state(da.loc[j]), ma_state(db.loc[j])
    m = (sa != "na") & (sb != "na")
    res = {
        "days": int(len(j)),
        "daily_ret_corr_nonroll": round(float(pd.Series(ra[ok]).corr(pd.Series(rb[ok]))), 4),
        "ma_state_agreement_pct": round(float((sa[m] == sb[m]).mean() * 100), 2),
        "ma_state_dist_spot": {k: int(v) for k, v in sa[m].value_counts().items()},
        "ma_state_dist_fut": {k: int(v) for k, v in sb[m].value_counts().items()},
    }
    # 15dk marubozu (O = L boğa / O = H ayı) sıklığı; vadelide gerçek tick fiyatı
    bu = md.load(fut, adjusted=False)
    pip = md.PIP[spot]
    for lab, d in [("spot", a), ("fut", bu)]:
        q = md.intraday(d, 15)
        q = q[q["n_min"] >= 14]
        body = q["close"] - q["open"]
        for tol_pip in [0.0, 0.5, 1.0]:
            tol = tol_pip * pip + EPS
            bull = (body > 0) & ((q["open"] - q["low"]) <= tol)
            bear = (body < 0) & ((q["high"] - q["open"]) <= tol)
            res[f"maru15_pct_{lab}_tol{tol_pip}"] = round(float((bull | bear).mean() * 100), 2)
    return res


def main() -> dict:
    res = {"integrity": {}, "release_spike_pip": {}, "days": {}, "coverage": {}, "rolls": {}, "proxy": {}}
    for n in INSTR:
        df = md.load(n)
        res["integrity"][n] = integrity(df)
        if n in ("EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "AUDUSD_FUT", "6E"):
            res["release_spike_pip"][n] = release_spike(df, md.PIP[n])
        if n in ("6E", "6B"):
            continue
        res["days"][n] = {b: day_structure(df, b) for b in ("tr", "ny17")}
        res.setdefault("day_quality", {})[n] = {}
        for b in ("tr", "ny17"):
            d = md.daily(df, b)
            q = md.day_quality(d, n)
            res["day_quality"][n][b] = {"days": int(len(d)), "bad": int((~q).sum()),
                                        "bad_list": [str(x.date()) for x in d.index[~q]]}
        res["coverage"][n] = {f"{m}m": intraday_coverage(df, m) for m in (15, 30)}
        print(n, "ok", flush=True)
    for n in ("AUDUSD_FUT", "USDJPY_FUT", "XAUUSD", "6E"):
        res["rolls"][n] = roll_check(n)
    res["proxy"]["6E~EURUSD"] = proxy_check("EURUSD", "6E")
    res["proxy"]["6B~GBPUSD"] = proxy_check("GBPUSD", "6B")
    res["proxy"]["6A~AUDUSD"] = proxy_check("AUDUSD", "AUDUSD_FUT")
    res["proxy"]["6J~USDJPY"] = proxy_check("USDJPY", "USDJPY_FUT")
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("release_spike_pip", "proxy")}, indent=1))
