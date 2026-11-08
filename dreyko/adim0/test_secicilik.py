"""secicilik.py testleri: sentetik doğruluk + gelecek barlar bozulunca bayraklar değişmez."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "faz0"))

import secicilik as S  # noqa: E402
from dreyko_data import derive_session_date  # noqa: E402


def _df(rows):
    df = pd.DataFrame(rows, columns=["t", "high", "low"]).set_index("t")
    df["session_date"] = derive_session_date(df.index)
    return df


def synth():
    T = pd.Timestamp
    rows = [(T("2023-03-13 18:00"), 110, 108), (T("2023-03-14 10:00"), 100, 90),   # önceki seans
            (T("2023-03-14 20:00"), 105, 100), (T("2023-03-14 22:00"), 101, 95),   # Asya 95-105
            (T("2023-03-15 03:00"), 104, 96), (T("2023-03-15 09:00"), 103, 97),
            (T("2023-03-15 09:30"), 99, 94),                                       # Asya low alındı
            (T("2023-03-15 09:40"), 98, 96),
            (T("2023-03-15 09:41"), 200, 1)]                                       # giriş barı (bilinmemeli)
    return _df(rows)


def test_levels_and_flags():
    df = synth()
    sb = S.session_bars(df)
    lv = S.levels(sb, pd.Series(10.0, index=list(sb)))
    d = pd.Timestamp("2023-03-15")
    r = lv.loc[d]
    assert (r.asia_hi, r.asia_lo, r.pd_hi, r.pd_lo) == (105, 95, 110, 90)
    em = 9 * 60 + 41
    assert S.flags(d, em, +1, sb, r) == {"F1": True, "F2": True, "F3": False}
    # short: Asya high/PDH alınmadı → F1 yok; Asya low alındı ama PDL açık → F2 var
    assert S.flags(d, em, -1, sb, r) == {"F1": False, "F2": True, "F3": False}
    # 09:30 barı girişten sonra olsaydı manipülasyon henüz yok
    assert S.flags(d, 9 * 60 + 30, +1, sb, r)["F1"] is False


def test_f1_requires_level_untaken_before_0930():
    df = synth()
    df.loc[pd.Timestamp("2023-03-15 03:00"), "low"] = 93       # Asya low 03:00'te alınmış
    sb = S.session_bars(df)
    r = S.levels(sb, pd.Series(10.0, index=list(sb))).loc[pd.Timestamp("2023-03-15")]
    assert S.flags(pd.Timestamp("2023-03-15"), 9 * 60 + 41, +1, sb, r)["F1"] is False


def test_asia_med_is_causal():
    idx = pd.date_range("2022-01-01", periods=100)
    lv_ratio = pd.Series(np.arange(100.0), index=idx)
    med = lv_ratio.expanding(min_periods=60).median().shift(1)
    assert np.isnan(med.iloc[59]) and med.iloc[60] == np.median(np.arange(60.0))


@pytest.fixture(scope="module")
def real():
    from dreyko_data import load_is
    df = load_is("NQ", ["open", "high", "low", "close"])
    df = df[(df.index >= "2023-01-01") & (df.index < "2023-04-01")]
    ev = pd.read_parquet(HERE / "out" / "events_NQ.parquet")
    ev = ev[(ev.date >= "2023-01-10") & (ev.date < "2023-04-01")]
    return df, ev


def test_perturbation_no_lookahead(real):
    df, ev = real
    sb = S.session_bars(df)
    lv = S.levels(sb, pd.Series(300.0, index=list(sb)))
    rng = np.random.default_rng(1)
    n = 0
    for _, e in ev.iterrows():
        if e.date not in sb:
            continue
        f0 = S.flags(e.date, int(e.entry_mod), int(e.d), sb, lv.loc[e.date])
        tm, h, l = sb[e.date]
        cut = S.day_base(e.date) + int(e.entry_mod)
        m = tm >= cut
        h2, l2 = h.copy(), l.copy()
        h2[m] = h2[m] * (1 + rng.normal(0, 0.02, m.sum())) + 50
        l2[m] = l2[m] * (1 - rng.normal(0, 0.02, m.sum())) - 50
        sb2 = dict(sb)
        sb2[e.date] = (tm, h2, l2)
        assert S.flags(e.date, int(e.entry_mod), int(e.d), sb2, lv.loc[e.date]) == f0
        n += 1
    assert n > 200
