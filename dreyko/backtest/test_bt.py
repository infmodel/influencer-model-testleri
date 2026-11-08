"""bt.py birim testleri: SL-first, boşluk, zaman çıkışı, limit dolum barı, hedef yönü."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "adim0"))

import bt  # noqa: E402
import events as E  # noqa: E402

D = pd.Timestamp("2023-03-15")


def day(rows):
    idx = pd.DatetimeIndex([D + pd.Timedelta(hours=r[0], minutes=r[1]) for r in rows])
    df = pd.DataFrame({"open": [r[2] for r in rows], "high": [r[3] for r in rows],
                       "low": [r[4] for r in rows], "close": [r[5] for r in rows]}, index=idx)
    return E.make_day(D, df)


def test_sl_first_same_bar():
    d = day([(10, 0, 100, 100, 100, 100), (10, 1, 100, 105, 95, 100)])
    assert bt.simulate(d, 0, 100, +1, 96, 104, False) == (96, "stop")
    assert bt.simulate(d, 0, 100, -1, 104, 96, False) == (104, "stop")


def test_gap_through_stop_exits_at_open():
    d = day([(10, 0, 100, 100, 100, 100), (10, 1, 94, 95, 93, 94)])
    assert bt.simulate(d, 0, 100, +1, 96, 104, False) == (94, "stop_gap")


def test_gap_through_target_exits_at_target():
    d = day([(10, 0, 100, 100, 100, 100), (10, 1, 106, 107, 105, 106)])
    assert bt.simulate(d, 0, 100, +1, 96, 104, False) == (104, "target_gap")


def test_time_exit_at_noon_open():
    d = day([(11, 58, 100, 101, 99, 100), (11, 59, 100, 101, 99, 100), (12, 0, 100.5, 101, 99, 100)])
    assert bt.simulate(d, 0, 100, +1, 90, 110, False) == (100.5, "time")


def test_limit_bar_target_not_counted():
    d = day([(10, 0, 100, 106, 99.5, 105), (10, 1, 105, 105, 104, 104), (12, 0, 103, 103, 103, 103)])
    assert bt.simulate(d, 0, 100, +1, 98, 104, True) == (104, "target_gap")  # hedef sonraki barın açılışında
    d2 = day([(10, 0, 100, 106, 97, 105), (12, 0, 103, 103, 103, 103)])
    assert bt.simulate(d2, 0, 100, +1, 98, 104, True) == (98, "stop")


def test_target_wrong_side_no_trade_and_risk_sign():
    ev = E.Event(D, "IFVG", "-", -1, 0, 0, "market", 100.0, 0, {"smt": 0.0},
                 {"ext": 101.0, "pm": (99.5, 98.0)})
    d = day([(10, 0, 100, 100.5, 99, 99.5), (12, 0, 99, 99, 99, 99)])
    t = bt.make_trade("NQ", d, None, ev, 1.0, "L")
    assert t is not None and t["tgt"] == 98.0 and t["stop"] == 101.25 and np.isclose(t["risk_pts"], 1.25)
    ev.refs["pm"] = (101.5, 100.5)            # short için hedef (PM low 100.5) girişin üstünde → işlem yok
    assert bt.make_trade("NQ", d, None, ev, 1.0, "L") is None
    ev.refs["ext"] = 99.0                      # stop girişin yanlış tarafında → işlem yok
    assert bt.make_trade("NQ", d, None, ev, 1.0, "R") is None


def test_cost_and_R():
    ev = E.Event(D, "IFVG", "-", 1, 0, 0, "market", 100.0, 0, {"smt": 1.0}, {"ext": 99.0, "pm": (110, 90)})
    d = day([(10, 0, 100, 103, 99.5, 102.5), (12, 0, 102, 102, 102, 102)])
    t = bt.make_trade("NQ", d, None, ev, 1.0, "R")       # risk 1.25, hedef 102.5 → 10:00 barında
    assert t["why"] == "target" and np.isclose(t["gross_pts"], 2.5)
    assert np.isclose(t["R"], (2.5 - 0.70) / 1.25) and np.isclose(t["usd"], (2.5 - 0.70) * 20)
