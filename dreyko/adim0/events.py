"""Adım 0 olay tespiti — Dreyko ilk tur (H1 FPFVG, H2 sweep+IFVG, H2b sweep+TS+CISD).

BACKTEST DEĞİLDİR: stop/hedef/maliyet yok. Yalnızca olay anını, karar anında bilinen
öznitelikleri ve olaydan sonraki ileri getirileri (etiket) üretir.

Zaman kuralları (faz0_rapor.md §7):
- Bar etiketi = bar açılışı. 09:30 barının OHLC'si 09:31:00'de bilinir.
- Market olaylar: tetik barı kapanınca karar, SONRAKİ barın açılışında giriş.
- Limit olay (FPFVG retest): emir FVG kenarında bekler; dokunan barda dolar,
  dolum fiyatı = kenar ya da (bar açılışı kenarın ötesindeyse) açılış.
- Tüm saatler America/New_York (veri indeksi datetime_ny, naive NY saati).

Proje kararları ve sonuçlardan önce sabitlenen ek tanımlar:
karar_gunlugu.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


def M(hh: int, mm: int) -> int:
    return hh * 60 + mm


PM_START, PM_END = M(8, 0), M(9, 29)       # 09:30 öncesi range: bar açılışları dahil
PM_MIN_BARS = 60                            # 90 dakikanın en az 60'ı olmalı
RTH_OPEN = M(9, 30)
SWEEP_END = M(9, 59)                        # sweep barı en geç 09:59 açılışlı
DEADLINE = M(11, 9)                         # IFVG / CISD tetik barı en geç 11:09 açılışlı
NOON = M(12, 0)
MACRO = (M(9, 50), M(10, 9))                # giriş barı açılışı bu aralıkta → makro içi
FPFVG_FIRST_BAR_MIN = M(9, 31)              # 3'lünün ilk barı en erken 09:31 (09:30 FVG'si hariç)
FPFVG_VARIANTS = {                          # (oluşum: 3. bar en geç, retest: bar en geç)
    "A": (M(9, 59), M(11, 9)),
    "B": (M(9, 44), M(10, 9)),
}
LEG_FVG_MIN = M(9, 0)                       # IFVG için sweep bacağı FVG'si: 3. bar en erken 09:00
HORIZONS = (15, 30, 60)
NS_PER_MIN = 60_000_000_000


@dataclass
class Day:
    date: pd.Timestamp
    tm: np.ndarray      # mutlak dakika (naive NY saatinin epoch dakikası), int64
    mod: np.ndarray     # gün içi dakika
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray

    @property
    def base(self) -> int:
        """Bu takvim gününün 00:00'ının mutlak dakikası."""
        return int(self.tm[0] - self.mod[0])

    def idx_at(self, mod: int) -> int:
        k = np.searchsorted(self.mod, mod)
        return int(k) if k < len(self.mod) and self.mod[k] == mod else -1

    def first_idx_from(self, tm_abs: int) -> int:
        """tm >= tm_abs olan ilk bar; yoksa -1."""
        k = np.searchsorted(self.tm, tm_abs, side="left")
        return int(k) if k < len(self.tm) else -1

    def last_idx_before(self, tm_abs: int) -> int:
        """tm < tm_abs olan son bar; yoksa -1."""
        return int(np.searchsorted(self.tm, tm_abs, side="left")) - 1

    def copy(self) -> "Day":
        return Day(self.date, self.tm.copy(), self.mod.copy(), self.o.copy(),
                   self.h.copy(), self.l.copy(), self.c.copy())


def make_day(date, df_day: pd.DataFrame) -> Day:
    idx = df_day.index
    tm = idx.asi8 // NS_PER_MIN
    mod = (idx.hour * 60 + idx.minute).to_numpy()
    return Day(pd.Timestamp(date), tm.astype(np.int64), mod.astype(np.int64),
               df_day["open"].to_numpy(float), df_day["high"].to_numpy(float),
               df_day["low"].to_numpy(float), df_day["close"].to_numpy(float))


# ---------------------------------------------------------------- FVG
@dataclass
class FVG:
    i: int          # 3. barın indeksi (FVG bu barın kapanışında kesinleşir)
    d: int          # +1 bullish, -1 bearish
    lo: float
    hi: float

    @property
    def near(self) -> float:
        """Geri testte fiyatın ilk değeceği kenar."""
        return self.hi if self.d > 0 else self.lo


def fvg_at(day: Day, i: int) -> FVG | None:
    """i'yi 3. bar kabul eden FVG. 3 bar ardışık dakika değilse None (eksik dakika kuralı)."""
    if i < 2 or day.tm[i] - day.tm[i - 2] != 2:
        return None
    if day.l[i] > day.h[i - 2]:
        return FVG(i, +1, day.h[i - 2], day.l[i])
    if day.h[i] < day.l[i - 2]:
        return FVG(i, -1, day.h[i], day.l[i - 2])
    return None


def first_fpfvg(day: Day, form_end: int) -> FVG | None:
    for i in range(2, len(day.tm)):
        if day.mod[i] > form_end:
            return None
        if day.mod[i - 2] < FPFVG_FIRST_BAR_MIN:
            continue
        f = fvg_at(day, i)
        if f is not None:
            return f
    return None


# ---------------------------------------------------------------- yardımcılar
def pm_range(day: Day):
    m = (day.mod >= PM_START) & (day.mod <= PM_END)
    if m.sum() < PM_MIN_BARS:
        return None
    return float(day.h[m].max()), float(day.l[m].min())


def took_levels(day: Day | None, pm, before_tm: int):
    """09:30'dan before_tm'e kadar (hariç) kapanmış barlarda PM high / low alındı mı."""
    if day is None or pm is None:
        return None
    m = (day.mod >= RTH_OPEN) & (day.tm < before_tm)
    if not m.any():
        return (False, False)
    return (bool(day.h[m].max() > pm[0]), bool(day.l[m].min() < pm[1]))


def smt_support(main: Day, other: Day | None, pm_main, pm_other, before_tm: int, d: int):
    """SMT: iki endeksten yalnız biri ilgili PM ucunu aldıysa.
    Bullish SMT (long'u destekler) = PM low'u yalnız biri aldı; bearish = PM high'ı yalnız biri.
    Dönen: 1/0, other yoksa NaN."""
    a = took_levels(main, pm_main, before_tm)
    b = took_levels(other, pm_other, before_tm)
    if a is None or b is None:
        return np.nan
    if d > 0:
        return float(a[1] != b[1])
    return float(a[0] != b[0])


def bearish(day: Day, k: int) -> bool:
    return day.c[k] < day.o[k]


def bullish(day: Day, k: int) -> bool:
    return day.c[k] > day.o[k]


def cisd_level(day: Day, e: int, side: int):
    """side=-1 (sellside sweep, dip): dibe götüren ardışık AYI mumlarının ilkinin açılışı.
    side=+1 (buyside sweep, tepe): tepeye götüren ardışık BOĞA mumlarının ilkinin açılışı.
    Dizi uç barında ya da bir önceki barda bitebilir. Bulunamazsa None."""
    against = bearish if side < 0 else bullish
    start = e if against(day, e) else (e - 1 if e - 1 >= 0 and day.tm[e] - day.tm[e - 1] == 1
                                       and against(day, e - 1) else -1)
    if start < 0:
        return None
    f = start
    while f - 1 >= 0 and day.tm[f] - day.tm[f - 1] == 1 and against(day, f - 1):
        f -= 1
    return float(day.o[f])


# ---------------------------------------------------------------- olaylar
@dataclass
class Event:
    date: pd.Timestamp
    event: str          # FPFVG_form, FPFVG_retest, SWEEP, IFVG, TSCISD
    variant: str        # A/B (FPFVG), '-' diğerleri
    d: int              # hipotezin doğal yönü (+1 long / -1 short)
    trig_idx: int       # karar barı (market: tetik barı; limit: dolum barı)
    entry_idx: int
    entry_kind: str     # market / limit
    entry_px: float
    info_tm: int        # bu andan (dahil) sonraki barlar karar bilgisine girmez
    feats: dict = field(default_factory=dict)
    refs: dict = field(default_factory=dict)   # backtest için karar anında bilinen seviyeler


def _market(day: Day, ev_name, variant, d, k, feats) -> Event | None:
    """k barının kapanışında karar → sonraki barın açılışında giriş."""
    dec = int(day.tm[k] + 1)
    e = day.first_idx_from(dec)
    if e < 0 or day.mod[e] >= NOON:
        return None
    return Event(day.date, ev_name, variant, d, k, e, "market", float(day.o[e]), dec, feats)


def detect_day(main: Day, other: Day | None, ctx: dict) -> list[Event]:
    """ctx: atr, prev_rth_close, prev2_rth_close, on_high, on_low (hepsi önceki/bugünkü 09:30 öncesi)."""
    out: list[Event] = []
    atr = ctx["atr"]
    if not np.isfinite(atr) or atr <= 0:
        return out
    i930 = main.idx_at(RTH_OPEN)
    if i930 < 0:
        return out
    pm = pm_range(main)
    pm_o = pm_range(other) if other is not None else None
    o930 = main.o[i930]

    def base_feats(ref_px: float, d: int, before_tm: int) -> dict:
        f = {
            "smt": smt_support(main, other, pm, pm_o, before_tm, d),
            "gap_atr": d * (o930 - ctx["prev_rth_close"]) / atr,
            "on_range_atr": (ctx["on_high"] - ctx["on_low"]) / atr,
            "prev_ret_atr": d * (ctx["prev_rth_close"] - ctx["prev2_rth_close"]) / atr,
        }
        if pm is not None:
            rng = pm[0] - pm[1]
            f["pm_range_atr"] = rng / atr
            f["pos_pm"] = d * (ref_px - (pm[0] + pm[1]) / 2) / rng if rng > 0 else np.nan
        else:
            f["pm_range_atr"] = np.nan
            f["pos_pm"] = np.nan
        return f

    # ---- H1: FPFVG oluşumu ve ilk geri testi
    for var, (form_end, retest_end) in FPFVG_VARIANTS.items():
        f = first_fpfvg(main, form_end)
        if f is None:
            continue
        i = f.i
        feats = base_feats(main.c[i], f.d, int(main.tm[i] + 1))
        feats["fvg_size_atr"] = (f.hi - f.lo) / atr
        ev = _market(main, "FPFVG_form", var, f.d, i, feats)
        if ev is not None:
            ev.feats["mins_since_open"] = int(main.mod[ev.entry_idx] - RTH_OPEN)
            leg = main.h[i930:i + 1].max() if f.d < 0 else main.l[i930:i + 1].min()
            ev.refs = {"fvg_i": i, "fvg_lo": f.lo, "fvg_hi": f.hi, "leg_ext": float(leg),
                       "retest_end": retest_end, "pm": pm}
            out.append(ev)
        for j in range(i + 1, len(main.tm)):
            if main.mod[j] > retest_end:
                break
            touched = main.l[j] <= f.hi if f.d > 0 else main.h[j] >= f.lo
            if touched:
                fill = min(main.o[j], f.hi) if f.d > 0 else max(main.o[j], f.lo)
                fr = base_feats(main.c[j - 1], f.d, int(main.tm[j]))
                fr["fvg_size_atr"] = (f.hi - f.lo) / atr
                fr["mins_since_open"] = int(main.mod[j] - RTH_OPEN)
                fr["wait_min"] = int(main.tm[j] - main.tm[i])
                out.append(Event(main.date, "FPFVG_retest", var, f.d, j, j, "limit",
                                 float(fill), int(main.tm[j] + 1), fr))
                break

    # ---- H2 / H2b: 08:00-09:30 range ucunun 09:30-10:00 arası süpürülmesi
    if pm is None or not (pm[1] <= o930 <= pm[0]):
        return out
    k0, side = -1, 0
    for k in range(i930, len(main.tm)):
        if main.mod[k] > SWEEP_END:
            break
        up, dn = main.h[k] > pm[0], main.l[k] < pm[1]
        if up and dn:
            return out          # aynı barda iki uç: belirsiz, olay yok
        if up or dn:
            k0, side = k, (+1 if up else -1)
            break
    if k0 < 0:
        return out
    d = -side                   # doğal yön: dönüş
    sf = base_feats(main.c[k0], d, int(main.tm[k0] + 1))
    ev = _market(main, "SWEEP", "-", d, k0, sf)
    if ev is not None:
        ev.feats["mins_since_open"] = int(main.mod[ev.entry_idx] - RTH_OPEN)
        out.append(ev)

    # H2: sweep bacağındaki son FVG'nin body kapanışla ters kırılması (IFVG)
    e = k0
    for k in range(k0 + 1, len(main.tm)):
        if main.mod[k] > DEADLINE:
            break
        if (main.h[k] > main.h[e]) if side > 0 else (main.l[k] < main.l[e]):
            e = k
        cand = None
        for q in range(e, -1, -1):
            if main.mod[q] < LEG_FVG_MIN:
                break
            fq = fvg_at(main, q)
            if fq is not None and fq.d == side:
                cand = fq
                break
        if cand is None:
            continue
        if (main.c[k] < cand.lo) if side > 0 else (main.c[k] > cand.hi):
            fi = base_feats(main.c[k], d, int(main.tm[k] + 1))
            fi["fvg_size_atr"] = (cand.hi - cand.lo) / atr
            fi["sweep_depth_atr"] = ((main.h[e] - pm[0]) if side > 0 else (pm[1] - main.l[e])) / atr
            ev = _market(main, "IFVG", "-", d, k, fi)
            if ev is not None:
                ev.refs = {"ext": float(main.h[e] if side > 0 else main.l[e]), "pm": pm}
                ev.feats["mins_since_open"] = int(main.mod[ev.entry_idx] - RTH_OPEN)
                out.append(ev)
            break

    # H2b: sweep → range içine kapanış (ilk tepki) → ilk sweep ucunun tekrar aşılması (TS)
    #      → TS ucuna götüren ardışık mumların ilkinin açılışı ötesinde body kapanış (CISD)
    ext = k0
    phase = "react"
    lvl = None
    for k in range(k0 + 1, len(main.tm)):
        if main.mod[k] > DEADLINE:
            break
        beyond = (main.h[k] > main.h[ext]) if side > 0 else (main.l[k] < main.l[ext])
        if phase == "react":
            if beyond:
                ext = k
            inside = (main.c[k] < pm[0]) if side > 0 else (main.c[k] > pm[1])
            if inside:
                phase = "ts"
            continue
        if phase == "ts":
            if beyond:
                ext = k
                phase = "cisd"
                lvl = cisd_level(main, ext, side)
            continue
        # phase == cisd
        if beyond:
            ext = k
            lvl = cisd_level(main, ext, side)
            continue
        if lvl is not None and ((main.c[k] < lvl) if side > 0 else (main.c[k] > lvl)):
            ft = base_feats(main.c[k], d, int(main.tm[k] + 1))
            ft["sweep_depth_atr"] = ((main.h[ext] - pm[0]) if side > 0 else (pm[1] - main.l[ext])) / atr
            ev = _market(main, "TSCISD", "-", d, k, ft)
            if ev is not None:
                ev.refs = {"ext": float(main.h[ext] if side > 0 else main.l[ext]), "pm": pm}
                ev.feats["mins_since_open"] = int(main.mod[ev.entry_idx] - RTH_OPEN)
                out.append(ev)
            break
    return out


# ---------------------------------------------------------------- etiket (gelecek!)
def price_at(day: Day, tm_abs: int, min_idx: int) -> float:
    """tm_abs'tan önce açılmış son barın kapanışı; o bar min_idx'ten önceyse NaN."""
    k = day.last_idx_before(tm_abs)
    return float(day.c[k]) if k >= min_idx else np.nan


def label(day: Day, ev: Event, atr: float) -> dict:
    """İleri getiriler (ATR birimi). ret_* = long yönlü ham getiri; dret_* = doğal yönde."""
    e = ev.entry_idx
    t0 = int(day.tm[e])
    out = {}
    targets = {f"h{h}": t0 + h for h in HORIZONS}
    targets["noon"] = day.base + NOON
    for name, T in targets.items():
        px = price_at(day, T, e)
        r = (px - ev.entry_px) / atr
        out[f"ret_{name}"] = r
        out[f"dret_{name}"] = ev.d * r
    s = e if ev.entry_kind == "market" else e + 1
    m = np.arange(len(day.tm)) >= s
    m &= day.tm < day.base + NOON
    if m.any():
        hi, lo = day.h[m].max(), day.l[m].min()
        fav = (hi - ev.entry_px) if ev.d > 0 else (ev.entry_px - lo)
        adv = (ev.entry_px - lo) if ev.d > 0 else (hi - ev.entry_px)
        out["mfe_noon"], out["mae_noon"] = max(fav, 0.0) / atr, max(adv, 0.0) / atr
    else:
        out["mfe_noon"], out["mae_noon"] = 0.0, 0.0
    return out


# ---------------------------------------------------------------- veri hazırlığı
def daily_context(df: pd.DataFrame) -> pd.DataFrame:
    """session_date başına: ATR(14) (yalnızca önceki tamamlanmış seanslar), önceki RTH kapanışları,
    bugünün 09:30 öncesi overnight high/low."""
    g = df.groupby("session_date")
    hi, lo, cl = g["high"].max(), g["low"].min(), g["close"].last()
    pc = cl.shift(1)
    tr = pd.concat([hi - lo, (hi - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14, min_periods=14).mean().shift(1)     # bugünün seansı DAHİL DEĞİL
    mod = df.index.hour * 60 + df.index.minute
    cal = df.index.normalize()
    sd = df["session_date"].to_numpy()
    rth = df[(mod >= RTH_OPEN) & (mod < M(16, 0)) & (cal == sd)]
    rc = rth.groupby("session_date")["close"].last()          # yalnızca RTH'li günler
    pre = df[~((cal == sd) & (mod >= RTH_OPEN))]               # 18:00 → 09:29
    gpre = pre.groupby("session_date")
    ctx = pd.DataFrame({
        "atr": atr,
        "prev_rth_close": rc.shift(1).reindex(hi.index),    # önceki RTH'li günün kapanışı
        "prev2_rth_close": rc.shift(2).reindex(hi.index),
        "on_high": gpre["high"].max().reindex(hi.index),
        "on_low": gpre["low"].min().reindex(hi.index),
    })
    return ctx


def build_days(df: pd.DataFrame, start=M(8, 0), end=M(13, 0)) -> dict:
    """session_date → Day (yalnızca seans gününün takvim tarihindeki start..end barları)."""
    mod = df.index.hour * 60 + df.index.minute
    cal = df.index.normalize()
    sub = df[(mod >= start) & (mod < end) & (cal == df["session_date"].to_numpy())]
    return {d: make_day(d, g) for d, g in sub.groupby("session_date")}
