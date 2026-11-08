"""bt.py testleri: sıralı işlem (çakışma yok), BE simülasyonu, metrikler, Wilson, DSR, pencereler."""
import numpy as np
import pandas as pd
import pytest

import bt
from bt import C


def toy(o, h, l, c):
    idx = pd.date_range("2024-07-02 06:00", periods=len(o), freq="1min", tz="UTC")
    df = pd.DataFrame({"open": o, "high": h, "low": l, "close": c}, index=idx, dtype=float)
    return C.make_inst("EURUSD", df, 1e-4, 1e-4)


def test_sequential_skips_overlap():
    n = 10
    g = toy([1.0] * n, [1.0005] * 4 + [1.003] + [1.0005] * 5, [0.9995] * n, [1.0] * n)
    ev = [{"model": "MX", "d": 1, "i0": 0, "entry": 1.0, "stop": 0.999, "tp": 1.002, "iend": 9, "fill_partial": False},
          {"model": "MX", "d": 1, "i0": 2, "entry": 1.0, "stop": 0.999, "tp": 1.002, "iend": 9, "fill_partial": False},
          {"model": "MX", "d": 1, "i0": 6, "entry": 1.0, "stop": 0.999, "tp": 1.002, "iend": 9, "fill_partial": False}]
    tr = bt.sequential(g, ev, "ny17")
    assert [t["i0"] for t in tr] == [0, 6]          # 2. olay 1. işlem açıkken (çıkış bar 4) atlandı
    assert tr[0]["exit_i"] == 4 and tr[0]["hit"] == 1
    assert tr[0]["R_net"] == pytest.approx(2 - 1e-4 / 1e-3)


def test_be_moves_stop_to_entry():
    # +1R (1.001) görülür, sonra fiyat girişe döner -> 0R
    g = toy([1.0, 1.0, 1.0005], [1.0005, 1.0011, 1.0006], [0.9995, 0.9999, 0.9998], [1.0, 1.001, 0.9999])
    R, ex = bt.simulate_be(g, 0, 1.0, 0.999, 1.0015, 1, 2, False)
    assert R == pytest.approx(0.0) and ex == 2


def test_be_sl_first_and_gap():
    g = toy([1.0, 0.997], [1.0005, 0.9975], [0.9995, 0.996], [1.0, 0.997])
    R, ex = bt.simulate_be(g, 0, 1.0, 0.999, 1.0015, 1, 1, False)
    assert R == pytest.approx(-3.0) and ex == 1


def test_wilson_and_maxdd():
    lo, hi = bt.wilson(50, 100)
    assert lo < 0.5 < hi and hi - lo == pytest.approx(0.192, abs=0.01)
    assert bt.max_dd(np.array([1, -1, -1, 2, -3.0])) == pytest.approx(3.0)
    assert bt.longest_loss_streak(np.array([1, -1, -1, 2, -3, -1, -1.0])) == 3


def test_dsr_monotone():
    a = bt.dsr(0.4, 500, 0.0, 3.0, 0.01, 50)   # SR0 ≈ 0.1 × 2.25 = 0.225
    b = bt.dsr(0.2, 500, 0.0, 3.0, 0.01, 50)   # beklenen maksimumun altında -> şişirilmiş
    assert a > 0.95 > b


def test_breakeven_cost():
    tr = pd.DataFrame({"R": [0.1, 0.1], "risk_pip": [10.0, 10.0]})
    assert bt.breakeven_cost_pip(tr) == pytest.approx(1.0)


def test_window_wr():
    t = pd.date_range("2020-01-01", periods=40, freq="5D", tz="UTC")
    tr = pd.DataFrame({"t_entry": t, "hit": [1.0] * 17 + [0.0] * 23})
    w = bt.window_wr(tr)
    assert w["win17_max"] == 1.0 and 0 < w["win17_ge_8824"] < 1


def test_fill_partial_inference():
    assert bt.fill_partial_of("MB-v") and bt.fill_partial_of("MD-4S-b") and bt.fill_partial_of("MC-B-1.0")
    assert not bt.fill_partial_of("MD-4S-a") and not bt.fill_partial_of("ME-1") and not bt.fill_partial_of("MC-A-1.0")
