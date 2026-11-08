"""MF: haftalık bias + PDH/PDL sweep + 15dk CHoCH (97GD). Ön kayıt §3."""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C

PIV_L = 2
LOOKBACK_DAYS = 5


def weekly_bias(inst: C.Inst, boundary: str, mode: str) -> dict:
    """Hafta Pazartesi'si -> o hafta için bias. mode: '1' (kararsız pas), '1k' (son kırılım devam), 'n' (yok)."""
    w = C.weeks(inst, boundary)
    H, L, Cl, ok = w["high"].to_numpy(), w["low"].to_numpy(), w["close"].to_numpy(), w["ok"].to_numpy()
    out = {}
    last = 0
    for j in range(1, len(w) - 1):
        if not (ok[j - 1] and ok[j]):
            last = 0
            continue
        b = 1 if Cl[j] > H[j - 1] else (-1 if Cl[j] < L[j - 1] else 0)
        if b != 0:
            last = b
        if mode == "1":
            v = b
        elif mode == "1k":
            v = b if b != 0 else last
        else:
            v = 2                      # iki yön
        if ok[j + 1] and v != 0:
            out[w.index[j + 1]] = v
    return out


class Piv15:
    """N dk pivotları (L=2) ve onay zamanları; likidite araması için."""

    def __init__(self, inst: C.Inst, minutes: int = 15, L: int = PIV_L):
        b = C.bars(inst, minutes)
        self.b = b
        self.minutes = minutes
        self.t = pd.DatetimeIndex(b.index).asi8
        self.h, self.l = b["high"].to_numpy(), b["low"].to_numpy()
        self.c, self.o = b["close"].to_numpy(), b["open"].to_numpy()
        ph, pl = C.pivots(self.h, self.l, L)
        self.L = L
        self.ph_idx = np.flatnonzero(ph)
        self.pl_idx = np.flatnonzero(pl)
        # pivot i, i+L barının kapanışında bilinir: onay zamanı = t[i+L] + 15dk
        n = len(self.t)
        self.ph_conf = self.t[np.minimum(self.ph_idx + L, n - 1)] + minutes * C.MIN
        self.pl_conf = self.t[np.minimum(self.pl_idx + L, n - 1)] + minutes * C.MIN

    def nearest_liq(self, inst: C.Inst, t_entry: int, entry: float, d: int, lookback_ns: int) -> float:
        """Girişten önce onaylanmış, girişe kadar (1dk çözünürlükte) alınmamış, girişin ötesindeki
        en yakın pivot. Yoksa NaN."""
        if d == 1:
            idx, conf, px, ser = self.ph_idx, self.ph_conf, self.h, inst.h
        else:
            idx, conf, px, ser = self.pl_idx, self.pl_conf, self.l, inst.l
        cand = idx[(conf <= t_entry) & (self.t[idx] >= t_entry - lookback_ns)]
        if len(cand) == 0:
            return np.nan
        lv = px[cand]
        cand = cand[(lv > entry) if d == 1 else (lv < entry)]
        e = np.searchsorted(inst.t, t_entry)
        for i in cand[np.argsort(np.abs(px[cand] - entry), kind="stable")]:
            a = np.searchsorted(inst.t, self.t[i] + self.minutes * C.MIN)
            part = ser[a:e]
            taken = (part >= px[i]).any() if d == 1 else (part <= px[i]).any()
            if not taken:
                return float(px[i])
        return np.nan


def mf_events(inst: C.Inst, boundary: str, mode: str, piv: Piv15 | None = None,
              sweep_atr: bool = False) -> list[dict]:
    d = C.days(inst, boundary)
    piv = piv or Piv15(inst)
    wb = weekly_bias(inst, boundary, mode)
    H, L, ok, atr = d["high"].to_numpy(), d["low"].to_numpy(), d["ok"].to_numpy(), d["atr"].to_numpy()
    bt = piv.t
    bh, bl, bc = piv.h, piv.l, piv.c
    evs = []
    for k in range(1, len(d)):
        date = d.index[k]
        wk = date - pd.Timedelta(days=date.dayofweek)
        if wk not in wb or not (ok[k] and ok[k - 1]) or not np.isfinite(atr[k]):
            continue
        dirs = [wb[wk]] if wb[wk] in (1, -1) else [1, -1]
        lim = 0.4 * atr[k] if (sweep_atr or inst.name == "XAUUSD") else 30 * inst.pip
        a_i, b_i = int(d["i0"].iat[k]), int(d["i1"].iat[k])
        t_a, t_b = inst.t[a_i], inst.t[b_i]
        j0, j1 = np.searchsorted(bt, t_a), np.searchsorted(bt, t_b, side="right")
        best = None
        for dirn in dirs:
            lvl = L[k - 1] if dirn == 1 else H[k - 1]
            ev = _scan(inst, piv, j0, j1, dirn, lvl, lim, b_i)
            if ev is not None and (best is None or ev["i0"] < best["i0"]):
                best = ev
        if best is None:
            continue
        t_e = inst.t[best["i0"]]
        tp = piv.nearest_liq(inst, int(t_e), best["entry"], best["d"], LOOKBACK_DAYS * 1440 * C.MIN)
        if not np.isfinite(tp) or best["d"] * (best["entry"] - best["stop"]) <= 0:
            continue
        k_end = min(k + 5, len(d) - 1)
        best.update({"model": f"MF-{mode}" + ("-atr" if sweep_atr else ""), "date": date, "tp": tp,
                     "iend": int(d["i1"].iat[k_end]), "fill_partial": True})
        evs.append(best)
    return evs


def _scan(inst, piv, j0, j1, dirn, lvl, lim, day_end_i):
    """Gün içi 15dk tarama: sweep -> CHoCH seviyesi -> 1dk'da seviyenin aşılması (stop-giriş)."""
    bh, bl, bc = piv.h, piv.l, piv.c
    swept = False
    m = -1
    ext = None
    level = None
    for j in range(j0, j1):
        if not swept:
            if (dirn == 1 and bl[j] < lvl) or (dirn == -1 and bh[j] > lvl):
                swept = True
            else:
                continue
        # sweep başladıktan sonra: önce bu barın 1dk'larında seviye dolumu (önceki bardan kalan seviye ile)
        if level is not None:
            a = np.searchsorted(inst.t, piv.t[j])
            b = min(np.searchsorted(inst.t, piv.t[j] + 15 * C.MIN) - 1, day_end_i)
            if b >= a:
                hh, ll, oo = inst.h[a:b + 1], inst.l[a:b + 1], inst.o[a:b + 1]
                if dirn == 1:
                    fill = C.first_true(hh >= level)
                    newx = C.first_true(ll < ext)
                else:
                    fill = C.first_true(ll <= level)
                    newx = C.first_true(hh > ext)
                if fill >= 0 and (newx < 0 or fill <= newx):
                    i0 = a + fill
                    entry = max(level, oo[fill]) if dirn == 1 else min(level, oo[fill])
                    return {"d": dirn, "i0": int(i0), "entry": float(entry), "stop": float(ext),
                            "depth_atr": np.nan}
        # bar kapandı: yeni uç mu?
        if (dirn == 1 and (ext is None or bl[j] < ext)) or (dirn == -1 and (ext is None or bh[j] > ext)):
            ext = bl[j] if dirn == 1 else bh[j]
            if abs(ext - lvl) > lim:
                return None                      # sweep çok derin -> gün iptal
            m = j
            s = m
            if dirn == 1:
                while s - 1 >= j0 and bh[s - 1] > bh[s]:
                    s -= 1
                level = bh[s:m + 1].max()
            else:
                while s - 1 >= j0 and bl[s - 1] < bl[s]:
                    s -= 1
                level = bl[s:m + 1].min()
    return None
