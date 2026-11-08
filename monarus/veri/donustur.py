"""bi5 gunluk dosyalari -> mevcut ham dosya bicimi (haftasonu kurali dahil).
Kural (EURUSD 2023 ile birebir dogrulandi):
 - Dukascopy gunluk dosyasi her zaman 1440 dakika dondurur (islem olmayan dakikalar duz O=H=L=C, hacim 0). Hafta ici bu duz barlar AYNEN korunur.
 - Cuma: haftasonu kapanisindan (17:00 New York = 22:00/21:00 UTC) itibaren barlar atilir. Cumartesi: tum barlar atilir.
 - Pazar: ilk hacimli bardan onceki duz barlar, o ilk hacimli barin CLOSE degeriyle doldurulur (mevcut dosyadaki davranis; ham Dukascopy Cuma kapanisini verir).
"""
import lzma, struct, os, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd
NY = ZoneInfo("America/New_York")
def fri_close_utc(day):
    return pd.Timestamp(dt.datetime(day.year, day.month, day.day, 17, tzinfo=NY)).tz_convert("UTC")
def decode_day(path, day, point, nd):
    raw = open(path, "rb").read()
    if not raw: return None
    b = lzma.decompress(raw)
    if not b: return None
    assert len(b) % 24 == 0
    a = np.frombuffer(b, dtype=np.dtype([("t", ">u4"), ("o", ">u4"), ("c", ">u4"), ("l", ">u4"), ("h", ">u4"), ("v", ">f4")]))
    ts = pd.Timestamp(day, tz="UTC") + pd.to_timedelta(a["t"].astype("int64"), unit="s")
    f = lambda k: np.round(a[k].astype("float64") * point, nd)
    return pd.DataFrame({"timestamp": ts, "open": f("o"), "high": f("h"), "low": f("l"), "close": f("c"), "v": a["v"].astype("float64")})
def transform(df, day):
    wd = day.weekday()
    if df is None or wd == 5: return None
    df = df.copy()
    if wd == 4:
        df = df[df.timestamp < fri_close_utc(day)]
    if wd == 6:
        nz = np.flatnonzero(df.v.values > 0)
        if len(nz):
            k = nz[0]; c = df.close.values[k]
            for col in ["open", "high", "low", "close"]: df.iloc[:k, df.columns.get_loc(col)] = c
    return df.drop(columns="v")
