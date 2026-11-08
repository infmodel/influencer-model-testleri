"""Adım 0 ortak araçları: enstrüman yükleme, günlük tablo + ATR, pivotlar, SL-first simülasyon, etiketler.

Ön kayıt: on_kayit.md §0. Yalnız IS (monarus_data._guard). Bar etiketi = açılış; 1dk bar i'nin bilgisi
t[i] + 1dk'da kesinleşir.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "faz0"))
import monarus_data as md  # noqa: E402

FX6 = ["EURUSD", "GBPUSD", "USDCAD", "USDCHF", "AUDUSD", "USDJPY"]
ALL7 = FX6 + ["XAUUSD"]
# Gidiş-dönüş maliyet, pip (XAU: 0,1 $ = 1 "pip"; NQ ayrı). AUD/JPY spot GEÇİCİ (ön kayıt §0).
COST_PIP = {"EURUSD": 1.0, "GBPUSD": 1.3, "USDCAD": 1.5, "USDCHF": 1.5, "AUDUSD": 1.3, "USDJPY": 1.3,
            "XAUUSD": 2.5}
PIP = dict(md.PIP)
MIN = np.int64(60_000_000_000)          # 1 dk, ns
TR_OFF = np.int64(3 * 3600 * 10**9)     # TR = UTC+3 sabit


@dataclass
class Inst:
    name: str
    df: pd.DataFrame
    t: np.ndarray            # int64 ns UTC, bar açılışı
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    pip: float
    cost: float              # fiyat birimi, gidiş-dönüş
    cache: dict = field(default_factory=dict)


def make_inst(name: str, df: pd.DataFrame, pip: float, cost: float) -> Inst:
    df = df[md.OHLC + [c for c in ("volume", "roll_flag") if c in df]].copy()
    t = df.index.asi8.astype(np.int64)
    return Inst(name, df, t, *(df[k].to_numpy(float) for k in md.OHLC), pip=pip, cost=cost)


def load_inst(name: str) -> Inst:
    df = md.load(name)
    return make_inst(name, df, PIP[name], COST_PIP[name] * PIP[name])


def tr_minute(t: np.ndarray) -> np.ndarray:
    """TR saatiyle günün dakikası (0..1439)."""
    return ((t + TR_OFF) // MIN) % 1440


# ---------------------------------------------------------------------------
# HTF tablolar
# ---------------------------------------------------------------------------
def _attach_idx(inst: Inst, b: pd.DataFrame) -> pd.DataFrame:
    b = b.copy()
    b["i0"] = np.searchsorted(inst.t, pd.DatetimeIndex(b["t_open"]).asi8)
    b["i1"] = np.searchsorted(inst.t, pd.DatetimeIndex(b["t_last"]).asi8)
    return b


def days(inst: Inst, boundary: str = "ny17") -> pd.DataFrame:
    """Günlük barlar + kalite + nedensel ATR14 (önceki günlerden) + 1dk indeks aralığı [i0, i1]."""
    key = ("days", boundary)
    if key in inst.cache:
        return inst.cache[key]
    d = md.daily(inst.df, boundary)
    d["ok"] = md.day_quality(d, inst.name).to_numpy()
    pc = d["close"].shift(1)
    tr = np.maximum(d["high"] - d["low"], np.maximum((d["high"] - pc).abs(), (d["low"] - pc).abs()))
    d["atr"] = tr.rolling(14).mean().shift(1)
    d["atr_pct60"] = d["atr"].rolling(60, min_periods=20).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
    d = _attach_idx(inst, d)
    d["k"] = np.arange(len(d))
    inst.cache[key] = d
    return d


def day_of_minute(inst: Inst, boundary: str = "ny17") -> np.ndarray:
    """Her 1dk barın günlük tablo satır numarası."""
    key = ("dom", boundary)
    if key not in inst.cache:
        d = days(inst, boundary)
        inst.cache[key] = np.searchsorted(d["i0"].to_numpy(), np.arange(len(inst.t)), side="right") - 1
    return inst.cache[key]


def bars(inst: Inst, minutes: int) -> pd.DataFrame:
    key = ("bars", minutes)
    if key not in inst.cache:
        b = md.intraday(inst.df, minutes)
        inst.cache[key] = _attach_idx(inst, b)
    return inst.cache[key]


def h4(inst: Inst, boundary: str = "ny17") -> pd.DataFrame:
    key = ("h4", boundary)
    if key not in inst.cache:
        inst.cache[key] = _attach_idx(inst, md.hours4(inst.df, boundary))
    return inst.cache[key]


def weeks(inst: Inst, boundary: str = "ny17") -> pd.DataFrame:
    """Haftalık barlar; ok = haftanın tüm günleri geçerli ve en az 4 gün."""
    key = ("weeks", boundary)
    if key in inst.cache:
        return inst.cache[key]
    d = days(inst, boundary)
    wk = d.index - pd.to_timedelta(d.index.dayofweek, unit="D")
    g = d.groupby(wk)
    w = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                      "close": g["close"].last(), "n_days": g.size(), "all_ok": g["ok"].all(),
                      "k_first": g["k"].first(), "k_last": g["k"].last()})
    w["ok"] = w["all_ok"] & (w["n_days"] >= 4)
    inst.cache[key] = w
    return w


# ---------------------------------------------------------------------------
# Yapı
# ---------------------------------------------------------------------------
def pivots(high: np.ndarray, low: np.ndarray, L: int):
    """Fraktal pivot: bar i, iki yanındaki L barın hepsinden kesin büyük (küçük). i+L'de bilinir."""
    n = len(high)
    ph = np.zeros(n, bool)
    pl = np.zeros(n, bool)
    if n < 2 * L + 1:
        return ph, pl
    from numpy.lib.stride_tricks import sliding_window_view as sw
    H = sw(high, 2 * L + 1)
    Lw = sw(low, 2 * L + 1)
    mid_h = H[:, L]
    mid_l = Lw[:, L]
    others_h = np.delete(H, L, axis=1)
    others_l = np.delete(Lw, L, axis=1)
    ph[L:n - L] = (mid_h[:, None] > others_h).all(axis=1)
    pl[L:n - L] = (mid_l[:, None] < others_l).all(axis=1)
    return ph, pl


def ma_state(H, L, C, H1, L1) -> str:
    """Model taslağı MA tablosu (faz0_checks.ma_state ile aynı öncelik)."""
    if not np.isfinite(H1):
        return "na"
    s = "na"
    if H <= H1 and L >= L1:
        s = "inside"
    if H > H1 and L < L1 and L1 <= C <= H1:
        s = "kararsiz"
    if C > H1:
        s = "flow_long"
    if C < L1:
        s = "flow_short"
    if H > H1 and C <= H1 and L >= L1:
        s = "crt_short"
    if L < L1 and C >= L1 and H <= H1:
        s = "crt_long"
    return s


BIAS = {"flow_long": 1, "crt_long": 1, "flow_short": -1, "crt_short": -1}


def state_series(b: pd.DataFrame) -> pd.Series:
    H, L, C = b["high"].to_numpy(), b["low"].to_numpy(), b["close"].to_numpy()
    H1 = np.r_[np.nan, H[:-1]]
    L1 = np.r_[np.nan, L[:-1]]
    return pd.Series([ma_state(*a) for a in zip(H, L, C, H1, L1)], index=b.index)


# ---------------------------------------------------------------------------
# SL-first simülasyon
# ---------------------------------------------------------------------------
def simulate(inst: Inst, i0: int, entry: float, stop: float, tp: float, d: int, iend: int,
             fill_partial: bool) -> dict:
    """i0: girişin olduğu 1dk bar. Market girişte entry = o[i0] ve bar tamamen girişten sonradır.
    Limit/stop dolumunda (fill_partial) dolum barında TP sayılmaz, stop sayılır.
    R = yönlü (çıkış - giriş) / risk. Süre sonunda açık -> c[iend] ile piyasa değeri."""
    risk = d * (entry - stop)
    if not (risk > 0) or iend < i0:
        return {"R": np.nan, "hit": np.nan, "resolved": False, "exit_i": -1, "mfe": np.nan, "mae": np.nan}
    hh, ll, oo = inst.h[i0:iend + 1], inst.l[i0:iend + 1], inst.o[i0:iend + 1]
    if d == 1:
        sl, tpm = ll <= stop, hh >= tp
    else:
        sl, tpm = hh >= stop, ll <= tp
    if fill_partial:
        tpm = tpm.copy()
        tpm[0] = False
    a = int(np.argmax(sl)) if sl.any() else 10**12
    b = int(np.argmax(tpm)) if tpm.any() else 10**12
    rtp = d * (tp - entry) / risk
    if a == b == 10**12:
        k = len(hh) - 1
        R = d * (inst.c[iend] - entry) / risk
        hit, res = 0.0, False
    elif a <= b:
        k = a
        px = stop
        if a > 0 and d * (oo[a] - stop) < 0:   # boşlukla stopun ötesinde açılış
            px = oo[a]
        R = d * (px - entry) / risk
        hit, res = 0.0, True
    else:
        k = b
        R = rtp
        hit, res = 1.0, True
    seg_h, seg_l = hh[:k + 1], ll[:k + 1]
    if d == 1:
        mfe, mae = (seg_h.max() - entry) / risk, (entry - seg_l.min()) / risk
    else:
        mfe, mae = (entry - seg_l.min()) / risk, (seg_h.max() - entry) / risk
    return {"R": float(R), "hit": hit, "resolved": res, "exit_i": i0 + k, "mfe": float(mfe), "mae": float(mae)}


def label_trade(inst: Inst, ev: dict, dtab: pd.DataFrame, dom: np.ndarray) -> dict:
    """Olay sözlüğüne SL-first, ayna, maliyet ve saat bazlı getiri etiketlerini ekler.
    ev: i0, entry, stop, tp, d, iend, fill_partial."""
    i0, entry, stop, tp, d, iend = ev["i0"], ev["entry"], ev["stop"], ev["tp"], ev["d"], ev["iend"]
    fp = ev.get("fill_partial", False)
    risk = d * (entry - stop)
    out = simulate(inst, i0, entry, stop, tp, d, iend, fp)
    rtp = d * (tp - entry) / risk
    mir = simulate(inst, i0, entry, entry + d * risk, entry - d * rtp * risk, -d, iend, fp)
    k = dom[i0]
    atr = dtab["atr"].iat[k]
    rec = {"R": out["R"], "hit": out["hit"], "resolved": out["resolved"], "mfe": out["mfe"], "mae": out["mae"],
           "rr": rtp, "risk_px": risk, "stop_atr": risk / atr if atr > 0 else np.nan,
           "R_net": out["R"] - inst.cost / risk, "cost_R": inst.cost / risk,
           "mR": mir["R"], "mhit": mir["hit"], "mR_net": mir["R"] - inst.cost / risk,
           "atr": atr, "atr_pct": dtab["atr_pct60"].iat[k]}
    rec["dR"] = rec["R"] - rec["mR"]
    rec["dhit"] = rec["hit"] - rec["mhit"]
    t0 = inst.t[i0]
    for name, mins in (("1h", 60), ("4h", 240)):
        j = np.searchsorted(inst.t, t0 + mins * MIN) - 1
        rec[f"ret_{name}"] = d * (inst.c[j] - entry) / atr if j >= i0 else np.nan
    je = int(dtab["i1"].iat[k])
    rec["ret_eod"] = d * (inst.c[je] - entry) / atr
    rec["tr_min"] = int(tr_minute(np.array([t0]))[0])
    return rec


def baseline_minute(inst: Inst, boundary: str = "ny17") -> pd.DataFrame:
    """Koşulsuz baz: her 1dk bar açılışından +1S, +4S ve gün sonuna long getiri / ATR; TR dakikasına göre ortalama."""
    key = ("base", boundary)
    if key in inst.cache:
        return inst.cache[key]
    d = days(inst, boundary)
    dom = day_of_minute(inst, boundary)
    atr = d["atr"].to_numpy()[dom]
    ok = d["ok"].to_numpy()[dom] & np.isfinite(atr) & (atr > 0)
    t, o, c = inst.t, inst.o, inst.c
    res = {}
    for name, mins in (("1h", 60), ("4h", 240)):
        j = np.searchsorted(t, t + mins * MIN) - 1
        res[name] = (c[j] - o) / atr
    res["eod"] = (c[d["i1"].to_numpy()[dom]] - o) / atr
    df = pd.DataFrame(res)[ok]
    df["m"] = tr_minute(t[ok])
    b = df.groupby("m").mean()
    inst.cache[key] = b
    return b


def add_excess(ev: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    for h in ("1h", "4h", "eod"):
        b = base[h].reindex(ev["tr_min"]).to_numpy()
        ev[f"x_{h}"] = ev[f"ret_{h}"] - ev["d"] * b
    return ev


def next_idx(inst: Inst, t_last_ns) -> int:
    """HTF barın son 1dk barı t_last ise, sonraki 1dk barın indeksi (market giriş)."""
    return int(np.searchsorted(inst.t, np.int64(t_last_ns), side="right"))


def first_true(mask: np.ndarray) -> int:
    return int(np.argmax(mask)) if mask.any() else -1
