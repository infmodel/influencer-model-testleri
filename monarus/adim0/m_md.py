"""MD: HTF FVG (POI) + 30dk pivot sweep + MSB; giriş MD-a (market) / MD-b (30dk FVG limiti). Ön kayıt §5."""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C
from m_mf import Piv15

PIV_L = 2
AGE_DAYS = 5
WAIT_BARS = 10
MIN_RR = 1.8
TR_LO, TR_HI = 9 * 60, 17 * 60       # MSB kapanışı TR dakikası (17:00 dahil)


def htf_fvgs(inst: C.Inst, boundary: str, htf: str) -> pd.DataFrame:
    """3 mumluk FVG'ler: yön, alt/üst, bilinme zamanı, geçersizleşme (dolma) ve yaş sonu zamanı."""
    b = C.h4(inst, boundary) if htf == "4S" else C.days(inst, boundary)
    if htf == "1G":
        b = b[b["ok"]]
    d = C.days(inst, boundary)
    dom = C.day_of_minute(inst, boundary)
    H, L = b["high"].to_numpy(), b["low"].to_numpy()
    i1 = b["i1"].to_numpy()
    rows = []
    for i in range(2, len(b)):
        for dirn, bot, top in ((1, H[i - 2], L[i]), (-1, H[i], L[i - 2])):
            if not top > bot:
                continue
            k_known = i1[i] + 1                 # bilinme: son 1dk barından sonraki bar
            if k_known >= len(inst.t):
                continue
            kd = dom[i1[i]]
            k_exp = min(kd + AGE_DAYS, len(d) - 1)
            e = int(d["i1"].iat[k_exp]) + 1      # yaş sonu (hariç)
            if dirn == 1:
                f = C.first_true(inst.l[k_known:e] < bot)
            else:
                f = C.first_true(inst.h[k_known:e] > top)
            inv = k_known + f if f >= 0 else e
            rows.append({"dir": dirn, "bot": bot, "top": top, "known_i": k_known, "end_i": inv,
                         "known_t": inst.t[k_known], "end_t": inst.t[min(inv, len(inst.t) - 1)] if inv < len(inst.t)
                         else np.iinfo(np.int64).max})
    return pd.DataFrame(rows).sort_values("known_t", kind="stable").reset_index(drop=True)


def md_events(inst: C.Inst, boundary: str, htf: str | None, entry: str, rr_filter: bool = True,
              piv30: Piv15 | None = None, tp_piv: Piv15 | None = None, tag: str = "") -> list[dict]:
    """htf: '4S' / '1G' / None (MD-n0). entry: 'a' (market) / 'b' (30dk FVG limiti)."""
    piv30 = piv30 or Piv15(inst, 30)
    tp_piv = tp_piv or piv30
    b30 = piv30.b
    t30 = piv30.t
    h, l, c = piv30.h, piv30.l, piv30.c
    n = len(t30)
    ph, pl = C.pivots(h, l, PIV_L)
    d = C.days(inst, boundary)
    dom = C.day_of_minute(inst, boundary)
    ok = d["ok"].to_numpy()
    tcm = C.tr_minute(t30 + 30 * C.MIN)
    fv = htf_fvgs(inst, boundary, htf) if htf else None
    if fv is not None:
        f_known, f_end = fv["known_t"].to_numpy(), fv["end_t"].to_numpy()
        f_dir, f_bot, f_top = fv["dir"].to_numpy(), fv["bot"].to_numpy(), fv["top"].to_numpy()
    evs = []
    used = set()
    dirs = [1, -1] if htf is None else [0]
    for want in dirs:
        poi = -1
        cands: list[int] = []
        sw = None      # (s, ext, msb_level)
        ptr = 0
        active: list[int] = []
        last_ph_i = last_pl_i = -1
        for j in range(n):
            tj = t30[j]
            q = j - PIV_L - 1       # bar j açılırken onaylı en son pivot: q+L <= j-1
            if q >= 0 and ph[q]:
                last_ph_i = q
            if q >= 0 and pl[q]:
                last_pl_i = q
            # POI belirle (bar j açılışında bilinen en güncel aktif FVG)
            if htf is not None:
                while ptr < len(fv) and f_known[ptr] <= tj:
                    active.append(ptr)
                    ptr += 1
                active = [z for z in active if f_end[z] > tj]
                cur = active[-1] if active else -1
                if cur != poi:
                    poi, cands, sw = cur, [], None
                if poi < 0:
                    continue
                dirn, bot, top = f_dir[poi], f_bot[poi], f_top[poi]
                # bölge içinde onaylanan pivotlar aday
                if q >= 0 and t30[q] >= f_known[poi]:
                    if dirn == 1 and pl[q] and bot <= l[q] <= top:
                        cands.append(q)
                    if dirn == -1 and ph[q] and bot <= h[q] <= top:
                        cands.append(q)
            else:
                dirn = want
                if q >= 0 and ((dirn == 1 and pl[q]) or (dirn == -1 and ph[q])):
                    cands = [q]          # n0: en son onaylı pivot
            # kurulum ömrü: sweep'ten sonra aynı türde yeni pivot onaylanırsa kurulum düşer
            # (ön kayıt açıklaması, sonuç görülmeden; karar günlüğü 8 Kas)
            if sw is not None and q > sw[0] and ((dirn == 1 and pl[q]) or (dirn == -1 and ph[q])):
                sw = None
            if sw is None:
                # sweep: fitille alıp içeride kapanış
                hit = None
                for p in cands:
                    lv = l[p] if dirn == 1 else h[p]
                    if (dirn == 1 and l[j] < lv <= c[j]) or (dirn == -1 and h[j] > lv >= c[j]):
                        hit = p
                        break
                if hit is not None:
                    ref = last_ph_i if dirn == 1 else last_pl_i
                    if ref >= 0:
                        sw = [j, l[j] if dirn == 1 else h[j], h[ref] if dirn == 1 else l[ref]]
                    cands = []
                continue
            s, ext, lvl = sw
            ext = min(ext, l[j]) if dirn == 1 else max(ext, h[j])
            sw[1] = ext
            if (dirn == 1 and c[j] > lvl) or (dirn == -1 and c[j] < lvl):
                sw = None
                if not (TR_LO <= tcm[j] <= TR_HI):
                    continue
                ev = _make_event(inst, piv30, b30, j, s, ext, dirn, entry, rr_filter, dom, d, tp_piv)
                if ev is None:
                    continue
                kd = dom[ev["i0"]]
                if kd < 0 or not ok[kd]:
                    continue
                ev.update({"model": f"MD-{htf or 'n0'}-{entry}" + ("" if rr_filter else "-n1") + tag,
                           "date": d.index[kd], "kd": int(kd),
                           "iend": int(d["i1"].iat[min(kd + 5, len(d) - 1)])})
                evs.append(ev)
    # gün başına ilk olay (giriş zamanına göre; n0'da iki yön birlikte)
    evs.sort(key=lambda e: e["i0"])
    out = []
    for ev in evs:
        if ev["kd"] in used:
            continue
        used.add(ev["kd"])
        out.append(ev)
    return out


def _make_event(inst, piv30, b30, j, s, ext, dirn, entry, rr_filter, dom, d, tp_piv):
    t30 = piv30.t
    i_msb = C.next_idx(inst, pd.Timestamp(b30["t_last"].iat[j]).value)
    if i_msb >= len(inst.t):
        return None
    if entry == "a":
        i0, px, fp = i_msb, inst.o[i_msb], False
    else:
        h, l = piv30.h, piv30.l
        lim = np.nan
        for i in range(j, s + 1, -1):           # MSB bacağındaki en son FVG
            if dirn == 1 and l[i] > h[i - 2] and i - 2 >= s:
                lim = l[i]
                break
            if dirn == -1 and h[i] < l[i - 2] and i - 2 >= s:
                lim = h[i]
                break
        if not np.isfinite(lim):
            return None
        e = np.searchsorted(inst.t, t30[j] + (30 + 30 * WAIT_BARS) * C.MIN) - 1
        seg_fill = inst.l[i_msb:e + 1] <= lim if dirn == 1 else inst.h[i_msb:e + 1] >= lim
        f = C.first_true(seg_fill)
        if f < 0:
            return None
        i0 = i_msb + f
        px = min(lim, inst.o[i0]) if dirn == 1 else max(lim, inst.o[i0])
        fp = True
    tp = tp_piv.nearest_liq(inst, int(inst.t[i_msb]), inst.o[i_msb], dirn, 5 * 1440 * C.MIN)
    if not np.isfinite(tp):
        return None
    if entry == "b":
        # dolumdan önce TP alınmışsa iptal
        pre = inst.h[i_msb:i0] if dirn == 1 else inst.l[i_msb:i0]
        if len(pre) and ((dirn == 1 and (pre >= tp).any()) or (dirn == -1 and (pre <= tp).any())):
            return None
    risk = dirn * (px - ext)
    if not risk > 0 or dirn * (tp - px) <= 0:
        return None
    rr = dirn * (tp - px) / risk
    if rr_filter and rr < MIN_RR:
        return None
    return {"d": dirn, "i0": int(i0), "entry": float(px), "stop": float(ext), "tp": float(tp), "fill_partial": fp}
