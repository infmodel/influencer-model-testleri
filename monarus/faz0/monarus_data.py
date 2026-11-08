"""Monarus projesi IS veri yükleyici ve yeniden örnekleyici (yalnızca 2020-2025).

Kaynak kuralları: ../../../data/CLAUDE.md. Veri dosyalarına YAZILMAZ.

Enstrümanlar (Monarus adı -> kaynak):
    EURUSD, GBPUSD, USDCAD, USDCHF : Dukascopy spot 1dk BID (data/, 5 hane)
    AUDUSD, USDJPY : Dukascopy spot 1dk BID, 8 Kasım 2026'da indirilip data/'ya eklendi (diğer 4 spotla
                     aynı işlenmiş şema; load_spot_ext ham yıllık dosyalardan bağımsız çapraz kontrol)
    AUDUSD_FUT : CME 6A 1dk vadeli (ratio back-adjusted, IS segmenti), yalnız çapraz kontrol
    USDJPY_FUT : CME 6J 1dk vadeli, 1/x çevrilir (high <-> low yer değiştirir), çapraz kontrol
    XAUUSD : CME GC 1dk vadeli (`*_adj` fark bazlı ayarlı seviye)
    6E, 6B : yalnızca spot<->vadeli vekil kalibrasyonu için
    NQ     : Dreyko yükleyicisi (session_date düzeltmeli), MC için

Zaman: bütün çıktıların indeksi UTC (tz-aware), bar etiketi = AÇILIŞ zamanı.
Gün sınırı seçenekleri (karar_gunlugu.md, kullanıcı):
    "tr"   : TR 00:00 (sabit UTC+3) = 21:00 UTC. Cumartesi'ye düşen kış saati
             Cuma kapanış artığı (21:00-22:00 UTC) Cuma gününe katılır.
    "ny17" : New York 17:00 (DST'li). Standart FX/CME işlem günü.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Veri kökü: TRADE_DATA_DIR ortam değişkeni (yoksa proje deposunun yanındaki data/ klasörü)
DATA = Path(os.environ.get("TRADE_DATA_DIR", Path(__file__).resolve().parents[3] / "data"))
SPOT = DATA / "FX_Currencies/dukascopy_spot/processed"
CME = DATA / "FX_Currencies/cme_futures/processed"
GC_IS = DATA / "GC_Gold/processed/GC_1m_IS_2020_2025.parquet"
IS_END = pd.Timestamp("2026-01-01", tz="UTC")
TR = "Europe/Istanbul"   # 2016'dan beri sabit UTC+3
NY = "America/New_York"

SPOT_PAIRS = {"EURUSD": "eurusd", "GBPUSD": "gbpusd", "USDCAD": "usdcad", "USDCHF": "usdchf",
              "AUDUSD": "audusd", "USDJPY": "usdjpy"}  # son ikisi 8 Kas 2026'da data/'ya eklendi
# Çapraz kontrol: AUDUSD/USDJPY ham yıllık dosyalarından doğrudan yükleme (load_spot_ext)
EXT_SPOT = DATA / "FX_Currencies/dukascopy_spot/raw"
EXT_PAIRS = {"AUDUSD": "audusd", "USDJPY": "usdjpy"}
FUT = {"AUDUSD_FUT": "6A", "USDJPY_FUT": "6J", "6E": "6E", "6B": "6B"}
INVERTED = {"USDJPY_FUT"}
# Pip büyüklüğü (Monarus'un kotasyonunda, yani USDJPY için yen)
PIP = {"EURUSD": 1e-4, "GBPUSD": 1e-4, "USDCAD": 1e-4, "USDCHF": 1e-4,
       "AUDUSD": 1e-4, "USDJPY": 1e-2, "AUDUSD_FUT": 1e-4, "USDJPY_FUT": 1e-2,
       "6E": 1e-4, "6B": 1e-4, "XAUUSD": 0.1}
TICK = {"AUDUSD_FUT": 5e-5, "6E": 5e-5, "6B": 1e-4, "USDJPY_FUT_raw": 5e-7, "XAUUSD": 0.1}

OHLC = ["open", "high", "low", "close"]


def _guard(idx: pd.DatetimeIndex) -> None:
    if idx.max() >= IS_END:
        raise ValueError("2026 (OOS) verisi yüklenmek üzere; IS dışına çıkılamaz")


def load_spot(pair: str) -> pd.DataFrame:
    f = SPOT / f"fx_dukas_{SPOT_PAIRS[pair]}_1m_processed.parquet"
    df = pd.read_parquet(f, columns=["ts_event", *OHLC, "is_oos_2026"])
    df = df[(~df["is_oos_2026"]) & (df["ts_event"] < IS_END)]
    df = df.set_index("ts_event")[OHLC].sort_index()
    df["volume"] = np.nan  # spot dosyasında hacim yok
    df["roll_flag"] = False
    _guard(df.index)
    return df


def market_hours(idx: pd.DatetimeIndex) -> np.ndarray:
    """Dukascopy ham -> işlenmiş kuralı (EURUSD/GBPUSD/USDCHF 2020-2025'te birebir doğrulandı):
    Cumartesi, Pazar NY 17:00 öncesi ve Cuma NY 17:00 sonrası (düz dolgu) barlar atılır."""
    ny = idx.tz_convert(NY)
    m = ny.hour * 60 + ny.minute
    d = ny.dayofweek
    return ~((d == 5) | ((d == 6) & (m < 17 * 60)) | ((d == 4) & (m >= 17 * 60)))


def load_spot_ext(pair: str) -> pd.DataFrame:
    files = sorted(EXT_SPOT.glob(f"{EXT_PAIRS[pair]}_20[2][0-5].parquet"))
    if len(files) != 6:
        raise FileNotFoundError(f"{pair}: {EXT_SPOT} altında 2020-2025 dosyaları eksik ({len(files)}/6)")
    df = pd.concat([pd.read_parquet(f) for f in files]).set_index("timestamp").sort_index()
    df = df[~df.index.duplicated()]
    df = df[(df.index < IS_END) & market_hours(df.index)][OHLC]
    df["volume"] = np.nan
    df["roll_flag"] = False
    _guard(df.index)
    return df


def invert_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    """1/x çevrimi: yeni high = 1/low, yeni low = 1/high."""
    out = df.copy()
    out["open"] = 1.0 / df["open"]
    out["close"] = 1.0 / df["close"]
    out["high"] = 1.0 / df["low"]
    out["low"] = 1.0 / df["high"]
    return out


def load_fut(name: str, adjusted: bool = True) -> pd.DataFrame:
    """CME FX vadeli, yalnızca IS segmenti.

    adjusted=True : ratio back-adjusted OHLC (çok günlü karşılaştırmalar roll'da sıçramaz).
    adjusted=False: gerçek kontrat fiyatı (`*_unadj`, tick ızgarasında).
    ATR/PDH gibi dosya kolonları KULLANILMAZ (ayarsızdır); her şey buradan yeniden hesaplanır.
    """
    sym = FUT[name]
    cols = ["ts_event", *OHLC, *(c + "_unadj" for c in OHLC), "volume", "roll_flag", "adj_segment"]
    df = pd.read_parquet(CME / f"fx_{sym}_1m_processed.parquet", columns=cols)
    df = df[(df["adj_segment"] == "IS") & (df["ts_event"] < IS_END)]
    df = df.set_index("ts_event").sort_index()
    if not adjusted:
        for c in OHLC:
            df[c] = df[c + "_unadj"]
    df = df[[*OHLC, "volume", "roll_flag"]]
    if name in INVERTED:
        df = invert_ohlc(df)
    _guard(df.index)
    return df


def load_gc() -> pd.DataFrame:
    """GC IS; seviye karşılaştırmaları için fark bazlı ayarlı `*_adj` (puan). Yüzde getiri için kullanmayın."""
    df = pd.read_parquet(GC_IS, columns=[c + "_adj" for c in OHLC] + ["volume", "is_roll_bar"])
    df = df.rename(columns={c + "_adj": c for c in OHLC}).rename(columns={"is_roll_bar": "roll_flag"})
    df = df.sort_index()
    _guard(df.index)
    return df


def load(name: str, **kw) -> pd.DataFrame:
    if name in SPOT_PAIRS:
        return load_spot(name)
    if name in EXT_PAIRS:
        return load_spot_ext(name)
    if name in FUT:
        return load_fut(name, **kw)
    if name == "XAUUSD":
        return load_gc()
    if name == "NQ":
        root = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(next((root / d / "faz0" for d in ("Dreyko", "dreyko") if (root / d / "faz0").exists()),
                                    root / "Dreyko/faz0")))
        from dreyko_data import load_is  # noqa: E402
        return load_is("NQ")
    raise KeyError(name)


# ---------------------------------------------------------------------------
# Gün / blok anahtarları
# ---------------------------------------------------------------------------
def day_key(idx: pd.DatetimeIndex, boundary: str = "tr") -> pd.DatetimeIndex:
    """Her 1dk barın ait olduğu işlem günü (tz'siz tarih).

    tr  : TR yerel tarihi; Cumartesi'ye düşen barlar Cuma'ya katılır.
    ny17: NY saati + 7 saat (17:00 NY -> ertesi gün 00:00) tarihi.
    """
    if boundary == "tr":
        loc = idx.tz_convert(TR).tz_localize(None)
        day = loc.normalize()
        sat = day.dayofweek == 5
        day = day.where(~sat, day - pd.Timedelta(days=1))
        return pd.DatetimeIndex(day)
    if boundary == "ny17":
        loc = idx.tz_convert(NY).tz_localize(None) + pd.Timedelta(hours=7)
        return pd.DatetimeIndex(loc.normalize())
    raise ValueError(boundary)


def block_key(idx: pd.DatetimeIndex, hours: int, boundary: str = "tr") -> pd.DatetimeIndex:
    """Gün içi N saatlik bloklar (4S: TR 00/04/08/12/16/20 ya da NY 17/21/01/05/09/13).

    Döner: blok başlangıcı (gün sınırına göre kaydırılmış yerel saat, tz'siz).
    """
    if boundary == "tr":
        loc = idx.tz_convert(TR).tz_localize(None)
    elif boundary == "ny17":
        loc = idx.tz_convert(NY).tz_localize(None) + pd.Timedelta(hours=7)
    else:
        raise ValueError(boundary)
    return pd.DatetimeIndex(loc.floor(f"{hours}h"))


def _agg(df: pd.DataFrame, key) -> pd.DataFrame:
    df = df.assign(_t=df.index)
    g = df.groupby(pd.Index(key), sort=True)
    out = pd.DataFrame({
        "open": g["open"].first(), "high": g["high"].max(),
        "low": g["low"].min(), "close": g["close"].last(),
        "n_min": g["close"].size(),
        "t_open": g["_t"].first(),
        "t_last": g["_t"].last(),
    })
    if "volume" in df:
        out["volume"] = g["volume"].sum(min_count=1)
    if "roll_flag" in df:
        out["has_roll"] = g["roll_flag"].any()
    return out


def daily(df: pd.DataFrame, boundary: str = "tr") -> pd.DataFrame:
    """Günlük barlar. İndeks = işlem günü tarihi. t_last = günün son 1dk barının açılışı (UTC);
    bar bilgisi t_last + 1dk'da kesinleşir."""
    return _agg(df, day_key(df.index, boundary))


def weekly(df: pd.DataFrame, boundary: str = "tr") -> pd.DataFrame:
    """Haftalık barlar (Pazartesi işlem günüyle başlayan hafta). İndeks = haftanın Pazartesi'si."""
    d = day_key(df.index, boundary)
    wk = d - pd.to_timedelta(d.dayofweek, unit="D")
    return _agg(df, wk)


def intraday(df: pd.DataFrame, minutes: int) -> pd.DataFrame:
    """UTC saat ızgarasına hizalı N dakikalık barlar (15/30/60). TR = UTC+3 tam saat
    olduğundan TR ızgarası ile aynıdır. Boş dakikalar doldurulmaz; n_min eksikliği gösterir."""
    out = _agg(df, df.index.floor(f"{minutes}min"))
    out.index = pd.DatetimeIndex(out.index, tz="UTC") if pd.DatetimeIndex(out.index).tz is None \
        else pd.DatetimeIndex(out.index)
    return out


def hours4(df: pd.DataFrame, boundary: str = "tr") -> pd.DataFrame:
    return _agg(df, block_key(df.index, 4, boundary))


# ---------------------------------------------------------------------------
# Gün kalitesi (Faz 0'da, sonuçlara bakılmadan sabitlendi)
# ---------------------------------------------------------------------------
MIN_MINUTES_FRAC = 0.80   # günün 1dk bar sayısı, enstrüman medyanının en az %80'i
MIN_VOLUME_FRAC = 0.25    # CME FX vadeli: günlük hacim, önceki 20 günün medyanının en az %25'i
# Hacim filtresi yalnız CME FX'te: roll öncesi Cumalar sürekli seri vadesi dolan ince kontratta
# kalıyor (hacim ~%20). GC (`GC.n.0`, açık pozisyon bazlı) roll öncesinde hacim düşse de
# dakika sayısı tam ve fiyat likit; orada hacim filtresi 86 sağlam günü atardı -> kapalı.
VOLUME_FILTER = {"AUDUSD_FUT": True, "USDJPY_FUT": True, "6E": True, "6B": True}


def day_quality(d: pd.DataFrame, name: str | None = None) -> pd.Series:
    """Günlük bar tablosu için geçerlilik bayrağı (True = kullanılabilir).

    - Eksik veri günleri (Dukascopy boşlukları, tatiller): n_min < %80 * medyan
    - Vadeli: roll öncesi ince kontrat günleri: hacim < %25 * önceki 20 gün medyanı
      (medyan yalnızca geçmiş günlerden, nedensel)
    - 2026'ya düşen günler (TR sınırında 31 Aralık 21:00 UTC sonrası artık) atılır
    Not: gün D'nin olay hesabı D-1'e de ihtiyaç duyar; çağıran taraf iki günü de kontrol eder.
    """
    ok = d["n_min"] >= MIN_MINUTES_FRAC * d["n_min"].median()
    if VOLUME_FILTER.get(name, False) and "volume" in d and d["volume"].notna().any():
        ref = d["volume"].shift(1).rolling(20, min_periods=5).median()
        ok &= ~(d["volume"] < MIN_VOLUME_FRAC * ref)
    ok &= pd.DatetimeIndex(d.index).year < 2026
    return ok
