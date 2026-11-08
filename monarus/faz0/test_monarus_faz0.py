"""Monarus Faz 0 testleri: yükleyici, gün/blok anahtarları, çevrim, nedensellik (pertürbasyon)."""
import numpy as np
import pandas as pd
import pytest

import monarus_data as md
from faz0_checks import ma_state


def utc(s):
    return pd.DatetimeIndex(pd.to_datetime(s, utc=True))


# --- gün sınırları ---------------------------------------------------------
def test_day_key_tr_midnight_is_2100_utc():
    k = md.day_key(utc(["2024-07-02 20:59", "2024-07-02 21:00"]), "tr")
    assert list(k.date.astype(str)) == ["2024-07-02", "2024-07-03"]


def test_day_key_tr_saturday_stub_goes_to_friday():
    # 2024-01-05 Cuma, kış: NY 17:00 = 22:00 UTC; 21:30 UTC = TR Cumartesi 00:30
    k = md.day_key(utc(["2024-01-05 21:30"]), "tr")
    assert str(k[0].date()) == "2024-01-05"


def test_day_key_tr_sunday_open_goes_to_monday():
    # Pazar açılışı 22:00 UTC (kış) = TR Pazartesi 01:00
    k = md.day_key(utc(["2024-01-07 22:00"]), "tr")
    assert str(k[0].date()) == "2024-01-08"


@pytest.mark.parametrize("ts,day", [
    ("2024-07-01 20:59", "2024-07-01"), ("2024-07-01 21:00", "2024-07-02"),   # EDT
    ("2024-01-02 21:59", "2024-01-02"), ("2024-01-02 22:00", "2024-01-03"),   # EST
])
def test_day_key_ny17_dst(ts, day):
    assert str(md.day_key(utc([ts]), "ny17")[0].date()) == day


def test_block_key_4h():
    # 01:00 UTC = 04:00 TR -> TR 04:00 bloğu; yaz: 01:00 UTC = 21:00 NY -> NY17 +7h = 04:00 bloğu
    assert md.block_key(utc(["2024-07-02 01:30"]), 4, "tr")[0] == pd.Timestamp("2024-07-02 04:00")
    assert md.block_key(utc(["2024-07-02 01:30"]), 4, "ny17")[0] == pd.Timestamp("2024-07-02 04:00")
    # kış: aynı UTC anı NY17'de bir saat geri kayar (03:30 -> 00:00 bloğu)
    assert md.block_key(utc(["2024-01-09 01:30"]), 4, "ny17")[0] == pd.Timestamp("2024-01-09 00:00")


# --- toplama ve çevrim -------------------------------------------------------
def _toy():
    idx = utc(pd.date_range("2024-07-02 20:55", periods=10, freq="1min"))
    o = np.arange(10, dtype=float) + 100
    return pd.DataFrame({"open": o, "high": o + 2, "low": o - 1, "close": o + 0.5,
                         "volume": 1.0, "roll_flag": False}, index=idx)


def test_daily_agg_matches_manual():
    df = _toy()
    d = md.daily(df, "tr")
    first = df.iloc[:5]   # 20:55-20:59 UTC -> 2 Temmuz
    r = d.loc[pd.Timestamp("2024-07-02")]
    assert r.open == first.open.iloc[0] and r.close == first.close.iloc[-1]
    assert r.high == first.high.max() and r.low == first.low.min() and r.n_min == 5
    assert r.t_last == first.index[-1]


def test_invert_swaps_high_low():
    df = _toy()
    inv = md.invert_ohlc(df)
    assert np.allclose(inv.high, 1 / df.low) and np.allclose(inv.low, 1 / df.high)
    assert (inv.high >= inv.low).all()


def test_ma_state_cases():
    d = pd.DataFrame({"high": [10, 11, 9.5, 12, 10.5, 9.9],
                      "low": [5, 6, 6.5, 4, 3, 3.5],
                      "close": [8, 10.8, 9, 9, 9, 3.6]},
                     index=pd.date_range("2024-01-01", periods=6))
    s = ma_state(d).tolist()
    # 2.gün: H>10, C<=10? hayır C=10.8>10 -> flow_long; 3.: inside; 4.: H>9.5,L<5.5,C=9 içeride -> kararsiz
    # 5.: H=10.5<=12, L=3<4, C=9>=4 -> crt_long; 6.: H 9.9<=10.5, L 3.5>=3 -> inside
    assert s == ["na", "flow_long", "inside", "kararsiz", "crt_long", "inside"]


def test_day_quality_flags_short_and_2026():
    d = pd.DataFrame({"n_min": [1440, 1440, 300, 1440], "volume": np.nan},
                     index=pd.to_datetime(["2025-12-29", "2025-12-30", "2025-12-31", "2026-01-01"]))
    assert md.day_quality(d, "EURUSD").tolist() == [True, True, False, False]


# --- gerçek veri: OOS koruması ve pertürbasyon -----------------------------------
@pytest.fixture(scope="module")
def eur():
    return md.load("EURUSD")


def test_no_oos_rows(eur):
    assert eur.index.max() < md.IS_END
    assert md.load("AUDUSD_FUT").index.max() < md.IS_END


def test_guard_raises():
    with pytest.raises(ValueError):
        md._guard(utc(["2026-01-02"]))


@pytest.mark.parametrize("boundary", ["tr", "ny17"])
def test_perturbation_future_bars_do_not_change_past(eur, boundary):
    """Karar anı t: t'den sonraki barları boz -> t'den önce TAMAMLANMIŞ günlük/4S/15dk barlar aynı kalmalı."""
    sub = eur.loc["2023-03-01":"2023-03-20"]
    t = pd.Timestamp("2023-03-10 12:07", tz="UTC")
    bad = sub.copy()
    m = bad.index >= t
    bad.loc[m, md.OHLC] = bad.loc[m, md.OHLC] * 1.5
    for f in (lambda x: md.daily(x, boundary), lambda x: md.hours4(x, boundary),
              lambda x: md.intraday(x, 15)):
        a, b = f(sub), f(bad)
        done = a["t_last"] < t   # bar t'den önce tamamlanmış
        pd.testing.assert_frame_equal(a[done], b.loc[a.index[done]])
        assert done.sum() > 5


def test_daily_equals_resample_of_shifted_index(eur):
    """Bağımsız yöntem: TR günü = UTC+3 kaydırılmış saatle pandas resample('D')."""
    sub = eur.loc["2023-05-01":"2023-05-31"]
    a = md.daily(sub, "tr")
    s = sub.copy()
    s.index = s.index.tz_convert(None) + pd.Timedelta(hours=3)
    b = s.resample("D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    b = b[b.index.dayofweek < 5]   # Cumartesi artığı yaz aylarında yok
    pd.testing.assert_frame_equal(a[md.OHLC], b.loc[a.index], check_names=False, check_freq=False)


def test_market_hours_rule():
    # Pazar 20:59 UTC (yaz, NY 16:59) atılır; 21:00 (NY 17:00) kalır; Cuma 21:00 UTC (yaz) atılır
    idx = utc(["2024-07-07 20:59", "2024-07-07 21:00", "2024-07-05 20:59", "2024-07-05 21:00", "2024-07-06 12:00"])
    assert md.market_hours(idx).tolist() == [False, True, True, False, False]


@pytest.mark.parametrize("pair", ["AUDUSD", "USDJPY"])
def test_ext_spot_is_only_and_clean(pair):
    df = md.load(pair)
    assert df.index.max() < md.IS_END and df.index.is_monotonic_increasing
    assert not df.index.duplicated().any()
    assert (df.high >= df.low).all()


@pytest.mark.parametrize("pair", ["AUDUSD", "USDJPY"])
def test_processed_matches_raw_years(pair):
    """Bağımsız yol: data/ işlenmiş dosyası = ham yıllık dosyalar + hafta sonu kuralı.
    Tek fark, 31 Ara 2025 NY17 sonrası (2026 işlem günü) barlar: işlenmişte OOS diye atılıyor."""
    a, b = md.load_spot(pair), md.load_spot_ext(pair)
    assert a.index.difference(b.index).empty
    extra = b.index.difference(a.index)
    assert (extra >= pd.Timestamp("2025-12-31 22:00", tz="UTC")).all() and len(extra) <= 120
    pd.testing.assert_frame_equal(a, b.loc[a.index])
