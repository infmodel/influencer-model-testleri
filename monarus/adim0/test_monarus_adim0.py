"""Adım 0 testleri: SL-first simülasyon, pivot, CRT/durum, ve her model için pertürbasyon (sızıntı) testi."""
import numpy as np
import pandas as pd
import pytest

import common as C
import m_ma
import m_mb
import m_mc
import m_md
import m_me
import m_mf


def toy_inst(o, h, l, c, start="2024-07-02 06:00"):
    idx = pd.date_range(start, periods=len(o), freq="1min", tz="UTC")
    df = pd.DataFrame({"open": o, "high": h, "low": l, "close": c}, index=idx, dtype=float)
    return C.make_inst("EURUSD", df, 1e-4, 1e-4)


# --- SL-first ----------------------------------------------------------------
def test_sim_tp_first():
    g = toy_inst([1.0, 1.0, 1.0], [1.001, 1.003, 1.0], [0.9995, 0.9995, 1.0], [1.0, 1.002, 1.0])
    r = C.simulate(g, 0, 1.0, 0.999, 1.002, 1, 2, False)
    assert r["hit"] == 1 and r["R"] == pytest.approx(2.0)


def test_sim_same_bar_sl_first():
    g = toy_inst([1.0], [1.005], [0.995], [1.0])
    r = C.simulate(g, 0, 1.0, 0.999, 1.002, 1, 0, False)
    assert r["hit"] == 0 and r["R"] == pytest.approx(-1.0)


def test_sim_gap_through_stop_exits_at_open():
    g = toy_inst([1.0, 0.997], [1.0005, 0.9975], [0.9995, 0.996], [1.0, 0.997])
    r = C.simulate(g, 0, 1.0, 0.999, 1.002, 1, 1, False)
    assert r["R"] == pytest.approx(-3.0)


def test_sim_fill_bar_tp_not_counted():
    g = toy_inst([1.001, 1.0], [1.003, 1.0], [1.0, 0.9985], [1.002, 0.999])
    r = C.simulate(g, 0, 1.0, 0.999, 1.002, 1, 1, True)
    assert r["hit"] == 0 and r["R"] == pytest.approx(-1.0)


def test_sim_short_and_mtm():
    g = toy_inst([1.0, 1.0], [1.0005, 1.0005], [0.9995, 0.9995], [1.0, 0.9996])
    r = C.simulate(g, 0, 1.0, 1.001, 0.998, -1, 1, False)
    assert not r["resolved"] and r["R"] == pytest.approx(0.4)


def test_pivots_strict():
    h = np.array([1, 2, 5, 2, 1, 3, 3, 1.0])
    l = h - 0.5
    ph, pl = C.pivots(h, l, 2)
    assert ph.tolist() == [False, False, True, False, False, False, False, False]
    assert pl[4]       # 0.5: sol 4.5, 1.5; sağ 2.5, 2.5 -> pivot low
    ph2, pl2 = C.pivots(np.array([3, 2, 1, 2, 3.0]), np.array([3, 2, 1, 2, 3.0]), 2)
    assert pl2.tolist() == [False, False, True, False, False]


def test_crt_dir():
    assert m_me.crt_dir(10, 5, 11, 6, 9) == -1     # high alındı, içeride kapanış
    assert m_me.crt_dir(10, 5, 9, 4, 6) == 1
    assert m_me.crt_dir(10, 5, 11, 4, 7) == 0      # iki uç
    assert m_me.crt_dir(10, 5, 11, 6, 10.5) == 0   # dışarıda kapanış


def test_ma_state_matches_faz0():
    import sys
    sys.path.insert(0, str(C.HERE.parent / "faz0"))
    from faz0_checks import ma_state as ref
    d = pd.DataFrame({"high": [10, 11, 9.5, 12, 10.5, 9.9, 11], "low": [5, 6, 6.5, 4, 3, 3.5, 3.6],
                      "close": [8, 10.8, 9, 9, 9, 3.6, 10]}, index=pd.date_range("2024-01-01", periods=7))
    assert C.state_series(d).tolist() == ref(d).tolist()


def test_wma():
    x = np.arange(1, 6, dtype=float)
    assert m_mb.wma(x, 3)[2] == pytest.approx((1 * 1 + 2 * 2 + 3 * 3) / 6)


# --- pertürbasyon -------------------------------------------------------------
T_CUT = pd.Timestamp("2023-05-10 13:07", tz="UTC")


@pytest.fixture(scope="module")
def pair():
    full = C.md.load("GBPUSD").loc["2022-06-01":"2023-06-30"]
    bad = full.copy()
    m = bad.index >= T_CUT
    rng = np.random.default_rng(1)
    k = rng.uniform(0.97, 1.03, m.sum())
    for col in C.md.OHLC:
        bad.loc[m, col] = bad.loc[m, col] * k
    bad.loc[m, "high"] = bad.loc[m, C.md.OHLC].max(axis=1)
    bad.loc[m, "low"] = bad.loc[m, C.md.OHLC].min(axis=1)
    a = C.make_inst("GBPUSD", full, 1e-4, 1.3e-4)
    b = C.make_inst("GBPUSD", bad, 1e-4, 1.3e-4)
    return a, b


def _decided(inst, evs):
    cut = T_CUT.value
    keys = ("model", "date", "d", "i0", "entry", "stop", "tp")
    return sorted(tuple(e[k] for k in keys) for e in evs if inst.t[e["i0"]] < cut)


MODELS = {
    "MA-T": lambda g: m_ma.ma_t_events(g, "ny17"),
    "ME-1": lambda g: m_me.me1_events(g, "ny17"),
    "ME-1n": lambda g: m_me.me1_events(g, "ny17", False),
    "ME-2": lambda g: m_me.me2_events(g, "ny17"),
    "MF-1": lambda g: m_mf.mf_events(g, "ny17", "1"),
    "MF-n": lambda g: m_mf.mf_events(g, "tr", "n"),
    "MB-v": lambda g: m_mb.mb_events(g, "v"),
    "MB-s": lambda g: m_mb.mb_events(g, "s"),
    "MD-4S-a-n1": lambda g: m_md.md_events(g, "ny17", "4S", "a", rr_filter=False),
    "MD-4S-b-n1": lambda g: m_md.md_events(g, "ny17", "4S", "b", rr_filter=False),
    "MD-1G-a-n1": lambda g: m_md.md_events(g, "tr", "1G", "a", rr_filter=False),
    "MD-n0-b": lambda g: m_md.md_events(g, "ny17", None, "b"),
}


@pytest.mark.parametrize("name", list(MODELS))
def test_perturbation(pair, name):
    a, b = pair
    ea, eb = MODELS[name](a), MODELS[name](b)
    da, db = _decided(a, ea), _decided(b, eb)
    assert da == db
    assert len(da) >= 1, f"{name}: kesimden önce olay yok, test anlamsız"


def test_perturbation_ma_bias(pair):
    a, b = pair
    xa, xb = m_ma.ma_days(a, "ny17"), m_ma.ma_days(b, "ny17")
    d = C.days(a, "ny17")
    # bias'ı belirleyen D günü kesimden önce bitmişse aynı olmalı
    done = d.index[pd.DatetimeIndex(d["t_last"]) < T_CUT]
    sa = xa.set_index("date")["bias"]
    sb = xb.set_index("date")["bias"]
    nxt = [d.index[d.index.get_loc(x) + 1] for x in done[:-1]]
    nxt = [x for x in nxt if x in sa.index and x in sb.index]
    assert len(nxt) > 50 and (sa.loc[nxt] == sb.loc[nxt]).all()


def test_mc_perturbation():
    g = m_mc.load_nq()
    sub = g.df.loc["2023-03-01":"2023-04-30"]
    cut = pd.Timestamp("2023-04-12 15:07", tz="UTC")
    bad = sub.copy()
    m = bad.index >= cut
    bad.loc[m, C.md.OHLC] = bad.loc[m, C.md.OHLC] * 1.02
    a = C.make_inst("NQ", sub, 0.25, 0.7)
    b = C.make_inst("NQ", bad, 0.25, 0.7)
    for v in ("A", "B"):
        ea = [(e["date"], e["d"], e["i0"], e["entry"], e["stop"]) for e in m_mc.mc_events(a, v, 0.01)
              if a.t[e["i0"]] < cut.value]
        eb = [(e["date"], e["d"], e["i0"], e["entry"], e["stop"]) for e in m_mc.mc_events(b, v, 0.01)
              if b.t[e["i0"]] < cut.value]
        assert ea == eb and len(ea) >= 2
