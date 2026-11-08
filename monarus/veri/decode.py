"""bi5 -> DataFrame. Kayit: >I zaman(sn), >I open, >I close, >I low, >I high, >f hacim."""
import lzma, struct, os, datetime as dt
import pandas as pd
def decode_day(path, day, point):
    raw = open(path, "rb").read()
    if not raw: return None
    b = lzma.decompress(raw)
    n = len(b) // 24
    assert n * 24 == len(b)
    rows = struct.iter_unpack(">IIIIIf", b)
    t, o, c, l, h, v = zip(*rows)
    base = pd.Timestamp(day, tz="UTC")
    ts = base + pd.to_timedelta(t, unit="s")
    return pd.DataFrame({"timestamp": ts, "open": [x*point for x in o], "high": [x*point for x in h],
                         "low": [x*point for x in l], "close": [x*point for x in c], "_v": v})
