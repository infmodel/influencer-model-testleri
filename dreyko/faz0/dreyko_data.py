"""Dreyko projesi için NQ/ES 1dk IS veri yükleyici.

- Yalnızca IS dosyaları (2020-2025). 2026 OOS dosyalarını OKUMAZ.
- `session_date` kolonu, processed dosyada DST bitiş pazarlarında (Kasım'ın ilk pazarı,
  18:00-23:59 NY) yanlış etiketli (pazartesi yerine pazar). Burada datetime_ny'den
  yeniden türetilir: NY saati >= 18:00 ise ertesi gün, değilse aynı gün.
- Orijinal kolon `session_date_src` olarak korunur. Veri dosyasına yazılmaz.
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(os.environ.get("TRADE_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))
IS_FILES = {
    "NQ": DATA / "NQ_Nasdaq/processed/nq_1m_continuous_2020_2025.parquet",
    "ES": DATA / "ES_SP500/processed/es_1m_continuous_2020_2025.parquet",
}
IS_END = pd.Timestamp("2026-01-01")


def derive_session_date(idx: pd.DatetimeIndex) -> np.ndarray:
    """CME işlem günü: NY 18:00 ve sonrası ertesi güne aittir."""
    mod = idx.hour * 60 + idx.minute
    day = idx.normalize()
    return np.where(mod >= 18 * 60, day + pd.Timedelta(days=1), day).astype("datetime64[ns]")


def load_is(sym: str, columns=None) -> pd.DataFrame:
    df = pd.read_parquet(IS_FILES[sym], columns=columns)
    if df.index.max() >= IS_END:
        raise ValueError("IS dosyasında 2026 verisi bulundu; OOS sızıntısı riski")
    if "session_date" in df.columns:
        df = df.rename(columns={"session_date": "session_date_src"})
    df["session_date"] = derive_session_date(df.index)
    return df
