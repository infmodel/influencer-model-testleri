import numpy as np
import pandas as pd

from faz0_checks import consecutive_triplets, expected_minutes, hm, minute_of_day, window_mask


def test_hm_and_expected():
    assert hm("09:30") == 570
    assert expected_minutes("09:30", "10:00") == 30
    assert expected_minutes("20:00", "00:00") == 240  # gece yarısını geçen pencere


def test_window_mask_overnight():
    mod = np.array([hm("19:59"), hm("20:00"), hm("23:59"), hm("00:00"), hm("09:30")])
    assert window_mask(mod, "20:00", "00:00").tolist() == [False, True, True, False, False]
    assert window_mask(mod, "09:30", "10:00").tolist() == [False, False, False, False, True]


def test_consecutive_triplets_detects_gap():
    idx = pd.DatetimeIndex(["2024-01-02 09:30", "2024-01-02 09:31", "2024-01-02 09:32",
                            "2024-01-02 09:34", "2024-01-02 09:35", "2024-01-02 09:36"])
    df = pd.DataFrame({"x": range(6)}, index=idx)
    r = consecutive_triplets(df, "09:30", "10:00")
    # 3'lüler (2. indeksten itibaren): 09:32 ok, 09:34 (gap) no, 09:35 no (09:33 yok), 09:36 ok -> 2/4
    assert abs(r["triplets_contiguous_share"] - 0.5) < 1e-9


def test_minute_of_day():
    idx = pd.DatetimeIndex(["2024-01-02 00:00", "2024-01-02 23:59"])
    assert minute_of_day(idx).tolist() == [0, 1439]


def test_derive_session_date_dst_sunday():
    from dreyko_data import derive_session_date
    idx = pd.DatetimeIndex(["2025-11-02 17:59", "2025-11-02 18:00", "2025-11-02 23:59",
                            "2025-11-03 00:00", "2025-11-03 09:30"])
    got = pd.DatetimeIndex(derive_session_date(idx))
    exp = pd.DatetimeIndex(["2025-11-02", "2025-11-03", "2025-11-03", "2025-11-03", "2025-11-03"])
    assert (got == exp).all()


def test_load_is_fixes_dst_sessions():
    from dreyko_data import load_is
    df = load_is("NQ", columns=["close", "session_date"])
    assert df.index.max() < pd.Timestamp("2026-01-01")
    w = df.loc["2025-11-02 18:00":"2025-11-02 23:59"]
    assert (w["session_date"] == pd.Timestamp("2025-11-03")).all()
    # Kaynakta hatalı olanlar dışında birebir aynı olmalı
    diff = (df["session_date"] != df["session_date_src"]).sum()
    assert diff == 6 * 360
