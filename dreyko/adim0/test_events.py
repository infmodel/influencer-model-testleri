"""events.py birim testleri + sızıntı (pertürbasyon) testi. Çalıştır: python -m pytest -q adim0"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "faz0"))

import events as E  # noqa: E402

DATE = pd.Timestamp("2023-03-15")


def synth(rows, date=DATE):
    """rows: list of (hh, mm, o, h, l, c)."""
    idx = pd.DatetimeIndex([date + pd.Timedelta(hours=r[0], minutes=r[1]) for r in rows])
    df = pd.DataFrame({"open": [r[2] for r in rows], "high": [r[3] for r in rows],
                       "low": [r[4] for r in rows], "close": [r[5] for r in rows]}, index=idx)
    return E.make_day(date, df)


def flat_pm(price=100.5, h=101.0, l=100.0):
    return [(8 + m // 60, m % 60, price, h, l, price) for m in range(90)]   # 08:00-09:29


SCENARIO = flat_pm() + [
    (9, 30, 100.5, 100.8, 100.4, 100.7),
    (9, 31, 100.7, 101.5, 100.7, 101.4),    # PM high (101) süpürüldü
    (9, 32, 101.4, 101.8, 101.0, 101.7),    # (09:30-09:32) bullish FVG 100.8-101.0
    (9, 33, 101.7, 101.75, 101.2, 101.3),
    (9, 34, 101.3, 101.35, 100.6, 100.7),   # body FVG altında → IFVG; range içine kapanış
    (9, 35, 100.7, 101.0, 100.6, 100.9),    # (09:33-09:35) bearish FVG 101.0-101.2 = FPFVG
    (9, 36, 100.9, 101.6, 100.85, 101.5),   # FPFVG retest (alt kenar 101.0)
    (9, 37, 101.5, 101.9, 101.45, 101.85),  # TS: 101.8 aşıldı
    (9, 38, 101.85, 101.86, 100.5, 100.6),  # CISD: 09:35 açılışı (100.7) altında kapanış
] + [(9 + (m + 39) // 60, (m + 39) % 60, 100.6, 100.6, 100.6, 100.6) for m in range(21 + 60 * 3)]

CTX = {"atr": 2.0, "prev_rth_close": 100.0, "prev2_rth_close": 99.0, "on_high": 101.0, "on_low": 99.5}


# ---------------------------------------------------------------- birim
def test_fvg_bull_bear_and_gap():
    d = synth([(9, 31, 1, 2, 1, 2), (9, 32, 2, 4, 2, 4), (9, 33, 4, 5, 3, 5)])
    f = E.fvg_at(d, 2)
    assert f.d == 1 and f.lo == 2 and f.hi == 3 and f.near == 3
    d = synth([(9, 31, 5, 6, 4, 4), (9, 32, 4, 4, 2, 2), (9, 33, 2, 3, 1, 1)])
    f = E.fvg_at(d, 2)
    assert f.d == -1 and f.lo == 3 and f.hi == 4 and f.near == 3
    d = synth([(9, 31, 1, 2, 1, 2), (9, 32, 2, 4, 2, 4), (9, 34, 4, 5, 3, 5)])   # 09:33 eksik
    assert E.fvg_at(d, 2) is None


def test_fpfvg_excludes_0930_first_bar_and_window():
    rows = [(9, 30, 1, 2, 1, 2), (9, 31, 2, 4, 2, 4), (9, 32, 4, 5, 3, 5),   # 09:30'lu 3'lü: sayılmaz
            (9, 33, 5, 5, 3.9, 4)]                                           # 09:31-09:33 FVG değil
    assert E.first_fpfvg(synth(rows), E.M(9, 59)) is None
    rows2 = [(9, 30, 1, 1, 1, 1)] + [(9, 31 + k, 1, 1, 1, 1) for k in range(14)] + [
        (9, 45, 1, 2, 1, 2), (9, 46, 2, 4, 1, 4), (9, 47, 4, 5, 3, 5)]
    d = synth(rows2)
    assert E.first_fpfvg(d, E.M(9, 44)) is None            # varyant B: 09:44'ten sonra
    assert E.first_fpfvg(d, E.M(9, 59)).i == d.idx_at(E.M(9, 47))


def test_pm_range_min_bars():
    assert E.pm_range(synth(flat_pm()[:59])) is None
    assert E.pm_range(synth(flat_pm())) == (101.0, 100.0)


def test_cisd_level():
    d = synth([(9, 40, 10, 10, 9, 9.5), (9, 41, 9.5, 9.6, 9, 9.2), (9, 42, 9.2, 9.3, 8, 8.5),
               (9, 43, 8.5, 9, 8.4, 8.9)])
    assert E.cisd_level(d, 2, -1) == 10       # ayı dizisi 09:40-09:42, ilkinin açılışı
    assert E.cisd_level(d, 3, -1) == 10       # uç barı boğa, dizi bir önceki barda bitiyor
    assert E.cisd_level(d, 0, +1) is None


def test_scenario_events():
    day = synth(SCENARIO)
    evs = {(e.event, e.variant): e for e in E.detect_day(day, None, CTX)}
    t = lambda hh, mm: day.idx_at(E.M(hh, mm))
    # FPFVG (bearish, 3. bar 09:35) → 09:36 açılışında market
    for v in "AB":
        f = evs[("FPFVG_form", v)]
        assert f.d == -1 and f.trig_idx == t(9, 35) and f.entry_idx == t(9, 36) and f.entry_px == 100.9
        r = evs[("FPFVG_retest", v)]
        assert r.entry_kind == "limit" and r.entry_idx == t(9, 36) and r.entry_px == 101.0
    s = evs[("SWEEP", "-")]
    assert s.d == -1 and s.trig_idx == t(9, 31) and s.entry_idx == t(9, 32)
    i = evs[("IFVG", "-")]
    assert i.d == -1 and i.trig_idx == t(9, 34) and i.entry_idx == t(9, 35) and i.entry_px == 100.7
    assert np.isclose(i.feats["fvg_size_atr"], 0.1)
    c = evs[("TSCISD", "-")]
    assert c.d == -1 and c.trig_idx == t(9, 38) and c.entry_idx == t(9, 39)
    assert np.isnan(s.feats["smt"])            # ES yok


def test_sweep_requires_open_inside_range():
    rows = flat_pm() + [(9, 30, 102, 103, 101.5, 102.5), (9, 31, 102.5, 104, 102, 103)]
    evs = E.detect_day(synth(rows), None, CTX)
    assert not [e for e in evs if e.event in ("SWEEP", "IFVG", "TSCISD")]


def test_smt_flags():
    main = synth(flat_pm() + [(9, 30, 100.5, 101.5, 100.4, 101)])     # PM high alındı
    oth_no = synth(flat_pm() + [(9, 30, 100.5, 100.9, 100.4, 100.8)])   # alınmadı
    oth_yes = synth(flat_pm() + [(9, 30, 100.5, 101.2, 100.4, 100.8)])
    pm = (101.0, 100.0)
    tm_after = int(main.tm[-1] + 1)
    assert E.smt_support(main, oth_no, pm, pm, tm_after, -1) == 1.0
    assert E.smt_support(main, oth_yes, pm, pm, tm_after, -1) == 0.0
    assert E.smt_support(main, oth_no, pm, pm, tm_after, +1) == 0.0      # low tarafı: ikisi de almadı
    assert E.smt_support(main, oth_no, pm, pm, int(main.tm[-1]), -1) == 0.0   # 09:30 barı henüz kapanmadı


def test_label_and_mfe():
    day = synth(SCENARIO)
    ev = [e for e in E.detect_day(day, None, CTX) if e.event == "IFVG"][0]
    lab = E.label(day, ev, CTX["atr"])
    # giriş 09:35 açılışı 100.7; 09:35+15dk → 09:49 barının kapanışı 100.6
    assert np.isclose(lab["ret_h15"], (100.6 - 100.7) / 2) and np.isclose(lab["dret_h15"], 0.05)
    assert np.isclose(lab["dret_noon"], 0.05)
    assert np.isclose(lab["mae_noon"], (101.9 - 100.7) / 2)     # 09:37 tepesi
    assert np.isclose(lab["mfe_noon"], (100.7 - 100.5) / 2)     # 09:38 dibi


def test_daily_context_atr_excludes_today():
    rows = []
    for k in range(20):
        d = pd.Timestamp("2023-01-02") + pd.Timedelta(days=k)
        for hh, mm in [(9, 30), (10, 0), (15, 59)]:
            rows.append((d + pd.Timedelta(hours=hh, minutes=mm), 100 + k, 101 + k, 99 + k, 100 + k))
    df = pd.DataFrame(rows, columns=["t", "open", "high", "low", "close"]).set_index("t")
    from dreyko_data import derive_session_date
    df["session_date"] = derive_session_date(df.index)
    a = E.daily_context(df)
    df2 = df.copy()
    last = df2.index[-1]
    df2.loc[last, "high"] = 1e6                 # son günü boz
    b = E.daily_context(df2)
    assert np.isfinite(a["atr"].iloc[-1]) and a["atr"].iloc[-1] == b["atr"].iloc[-1]
    assert np.isnan(a["atr"].iloc[13]) and np.isfinite(a["atr"].iloc[14])
    assert a["prev_rth_close"].iloc[-1] == 100 + 18


# ---------------------------------------------------------------- sızıntı (gerçek veri)
@pytest.fixture(scope="module")
def real():
    from dreyko_data import load_is
    cols = ["open", "high", "low", "close"]
    nq, es = load_is("NQ", cols), load_is("ES", cols)
    sel = lambda df: df[(df.index >= "2022-01-01") & (df.index < "2022-07-01")]
    nq, es = sel(nq), sel(es)
    return E.build_days(nq), E.build_days(es), E.daily_context(nq)


def _perturb(day, from_tm, rng, only_close_idx=None):
    d = day.copy()
    if only_close_idx is not None:
        d.c[only_close_idx] *= 1 + rng.normal(0, 0.01)
        return d
    m = d.tm >= from_tm
    if not m.any():
        return d
    for arr in (d.o, d.h, d.l, d.c):
        arr[m] = arr[m] * (1 + rng.normal(0, 0.01, m.sum()))
    d.h[m] = np.maximum.reduce([d.o[m], d.h[m], d.l[m], d.c[m]])
    d.l[m] = np.minimum.reduce([d.o[m], d.h[m], d.l[m], d.c[m]])
    return d


def _same(a, b):
    assert (a.d, a.trig_idx, a.entry_idx, a.entry_kind) == (b.d, b.trig_idx, b.entry_idx, b.entry_kind)
    if a.entry_kind == "limit":     # market giriş = karar SONRASI ilk açılış; pertürbe edilmesi beklenir
        assert a.entry_px == b.entry_px
    assert a.feats.keys() == b.feats.keys()
    for k in a.feats:
        x, y = a.feats[k], b.feats[k]
        assert (np.isnan(x) and np.isnan(y)) or x == y, k


def test_perturbation_no_lookahead(real):
    nq_days, es_days, ctx = real
    rng = np.random.default_rng(0)
    n_checked = 0
    for date, day in list(nq_days.items()):
        c = ctx.loc[date].to_dict()
        other = es_days.get(date)
        base = E.detect_day(day, other, c)
        for ev in base:
            p_main = _perturb(day, ev.info_tm, rng)
            p_oth = _perturb(other, ev.info_tm, rng) if other is not None else None
            again = {(e.event, e.variant): e for e in E.detect_day(p_main, p_oth, c)}
            _same(ev, again[(ev.event, ev.variant)])
            n_checked += 1
            if ev.entry_kind == "limit":       # dolum barının kapanışı özniteliklere sızmamalı
                p2 = _perturb(day, 0, rng, only_close_idx=ev.entry_idx)
                again2 = {(e.event, e.variant): e for e in E.detect_day(p2, other, c)}
                _same(ev, again2[(ev.event, ev.variant)])
    assert n_checked > 200
