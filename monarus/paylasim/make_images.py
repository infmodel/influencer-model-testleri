"""X paylaşımı ve README için 4 görsel (1600x900). Veri: adim0/out ve backtest/out (IS 2020-2025)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"   # kategorik sıra (doğrulandı)
CRIT = "#d03b3b"
BAND = "#e3e2de"
plt.rcParams.update({"font.family": ["Noto Sans", "DejaVu Sans"], "text.color": INK, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": GRID})
W, H, DPI = 8, 4.5, 200
FOOT = "Veri: Dukascopy spot FX, CME GC ve NQ 1 dk, 2020–2025 · Yalnızca videolarda anlatılan kurallar test edildi"


def fig():
    return plt.figure(figsize=(W, H), dpi=DPI, facecolor=SURF)


def footer(f, extra=None):
    f.text(0.04, 0.035, FOOT if extra is None else extra, fontsize=6.3, color=MUTED)


def save(f, name):
    f.savefig(OUT / name, facecolor=SURF, dpi=DPI)
    plt.close(f)


def summ():
    return pd.read_csv(ROOT / "backtest/out/summary.csv")


def row(s, model, inst, b="ny17"):
    return s[(s.model == model) & (s.inst == inst) & (s.boundary == b)].iloc[0]


# ------------------------------------------------------------- 1. kapak
def cover():
    s = summ()
    mb = row(s, "MB-v", "POOL_CLAIM")
    f = fig()
    f.text(0.04, 0.88, "Monarus'un YouTube'da anlattığı 6 trade modelini", fontsize=17, weight="bold")
    f.text(0.04, 0.80, "6 yıllık gerçek veride test ettik.", fontsize=17, weight="bold")
    f.text(0.04, 0.715, "Sonuç: Videolardaki kuralların hiçbiri kârlı değil. İddia edilen kazanma oranları çıkmıyor.",
           fontsize=9.5, color=INK2)
    tiles = [(f"{int(s[~s.inst.str.startswith('POOL')].n.sum()):,}".replace(",", "."), "simüle edilen işlem\n(7 enstrüman + NQ, 2020–2025)"),
             ("0 / 260", "backtest satırından\nkârlılık şartını geçen"),
             (f"%{mb.wr * 100:.0f}", "marubozu 1:1 modelinin\nkazanma oranı\n(iddia: \"%75'in altına düşmedim\")")]
    x0, w, gap = 0.04, 0.287, 0.0245
    for i, (big, small) in enumerate(tiles):
        x = x0 + i * (w + gap)
        f.patches.append(FancyBboxPatch((x, 0.28), w, 0.34, boxstyle="round,pad=0,rounding_size=0.015",
                                        transform=f.transFigure, facecolor="#f0efec", edgecolor="none"))
        f.text(x + 0.025, 0.465, big, fontsize=30, weight="bold", color=CRIT if i else INK)
        f.text(x + 0.025, 0.42, small, fontsize=8.5, color=INK2, va="top", linespacing=1.35)
    footer(f)
    save(f, "1_sonuc.png")


# ------------------------------------------------------------- 2. iddia vs ölçülen
def claims():
    s = summ()
    rows = [("Marubozu 1:1 (MB)\nGBPUSD, AUDUSD, USDJPY", row(s, "MB-v", "POOL_CLAIM"), (0.75, 0.88)),
            ("Fon sistemi (MF)\nhaftalık bias + PDH/PDL + CHoCH", row(s, "MF-1", "POOL"), (0.68, 0.80)),
            ("Ana model (MD)\nFVG + 30dk MSB, min 1,8R", row(s, "MD-4S-a", "POOL"), (0.75, 0.75)),
            ("Ana model (MD)\n1,8R şartı olmadan", row(s, "MD-4S-a-n1", "POOL"), (0.75, 0.75))]
    f = fig()
    f.text(0.04, 0.89, "İddia edilen kazanma oranı ile ölçülen", fontsize=16, weight="bold")
    f.text(0.04, 0.815, "Gri: videoda söylenen oran · Mavi: aynı kurallarla 6 yılda ölçülen (%95 güven aralığı) · "
           "Siyah çizgi: başa baş oranı (RR'ye göre)", fontsize=8, color=INK2)
    ax = f.add_axes([0.36, 0.16, 0.6, 0.58], facecolor=SURF)
    ys = np.arange(len(rows))[::-1]
    for y, (lab, r, (c0, c1)) in zip(ys, rows):
        ax.barh(y, max(c1 - c0, 0.012), left=c0 - (0.006 if c1 == c0 else 0), height=0.42, color=BAND,
                edgecolor="none", zorder=1)
        ax.plot([r.wr_lo, r.wr_hi], [y, y], color=S1, lw=2, solid_capstyle="round", zorder=3)
        ax.plot(r.wr, y, "o", ms=7, color=S1, mec=SURF, mew=1.5, zorder=4)
        ax.plot([r.be_wr, r.be_wr], [y - 0.28, y + 0.28], color=INK, lw=1.4, zorder=2)
        ax.text(r.wr, y + 0.27, f"%{r.wr * 100:.0f}", fontsize=7.5, ha="center", va="bottom", color=INK)
        claim = f"iddia %{c0 * 100:.0f}" + (f"–{c1 * 100:.0f}" if c1 != c0 else "")
        ax.text(c1 + 0.012, y, claim, fontsize=7, va="center", color=INK2)
        f.text(0.04, 0.16 + 0.58 * (y + 0.5) / len(rows), lab, fontsize=7.8, va="center", linespacing=1.3)
        f.text(0.335, 0.16 + 0.58 * (y + 0.5) / len(rows), f"n={int(r.n)}", fontsize=6.8, va="center",
               ha="right", color=MUTED)
    ax.set_xlim(0.1, 1.0)
    ax.set_xticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xticklabels(["%20", "%40", "%60", "%80", "%100"], fontsize=7)
    ax.set_yticks([])
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    footer(f, FOOT + " · maliyet dahil, aynı mumda stop ve hedef görülürse stop")
    save(f, "2_iddia_olculen.png")


# ------------------------------------------------------------- 3. günlük bias isabeti
def bias():
    m = pd.read_csv(ROOT / "adim0/out/ma_stats.csv")
    m = m[(m.boundary == "ny17") & (m.subset == "tümü")].set_index("inst")
    order = ["EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "USDJPY", "XAUUSD"]
    claim = {"EURUSD": 0.719, "GBPUSD": 0.669, "AUDUSD": 0.668, "USDCAD": 0.801, "USDCHF": 0.683, "XAUUSD": 0.607}
    f = fig()
    f.text(0.04, 0.89, "Günlük bias isabeti: rakam doğru, ama yön bilgisi yok", fontsize=16, weight="bold")
    f.text(0.04, 0.815, "Ertesi gün bias hedefine değme oranı (mavi), aynı mesafede TERS yöndeki seviyeye değme oranı (turuncu) "
           "ve iddia (gri)", fontsize=8, color=INK2)
    ax = f.add_axes([0.08, 0.17, 0.88, 0.56], facecolor=SURF)
    x = np.arange(len(order))
    w = 0.26
    hb = [m.at[i, "hit_bias"] for i in order]
    hm = [m.at[i, "hit_mirror"] for i in order]
    ax.bar(x - w / 2 - 0.01, hb, w, color=S1, zorder=2)
    ax.bar(x + w / 2 + 0.01, hm, w, color=S2, zorder=2)
    for xi, i in zip(x, order):
        if i in claim:
            ax.plot([xi - 0.36, xi + 0.36], [claim[i]] * 2, color=MUTED, lw=1.6, ls=(0, (2, 1.5)), zorder=3)
        ax.text(xi - w / 2 - 0.01, m.at[i, "hit_bias"] + 0.012, f"%{m.at[i, 'hit_bias'] * 100:.0f}", ha="center",
                fontsize=6.6, color=INK)
        ax.text(xi + w / 2 + 0.01, m.at[i, "hit_mirror"] + 0.012, f"%{m.at[i, 'hit_mirror'] * 100:.0f}", ha="center",
                fontsize=6.6, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(order, fontsize=7.5)
    ax.set_ylim(0, 0.92)
    ax.set_yticks([0, 0.25, 0.5, 0.75])
    ax.set_yticklabels(["%0", "%25", "%50", "%75"], fontsize=7)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    f.text(0.08, 0.755, "■ bias hedefine değme", color=S1, fontsize=7.5)
    f.text(0.27, 0.755, "■ ters yönde aynı mesafeye değme", color=S2, fontsize=7.5)
    f.text(0.52, 0.755, "┅ Monarus'un tablosu", color=MUTED, fontsize=7.5)
    footer(f, FOOT + " · hedef kapanışa medyan 0,2 ATR uzakta; bias yönünde gün sonu getirisi ≈ 0")
    save(f, "3_bias_isabeti.png")


# ------------------------------------------------------------- 4. backtest equity
def equity():
    tr = pd.read_parquet(ROOT / "backtest/out/trades.parquet")
    tr = tr[tr.boundary == "ny17"]
    series = [("MB-v", ["GBPUSD", "AUDUSD", "USDJPY"], "Marubozu 1:1 (MB)", S1),
              ("MF-1", None, "Fon sistemi (MF)", S2),
              ("ME-1", None, "Bias + 4S CRT (ME)", S3),
              ("MA-T", None, "Bias + 1S giriş (MA)", S4)]
    f = fig()
    f.text(0.04, 0.89, "Backtest: dört ana modelin dördü de 6 yıl sonunda zararda", fontsize=16, weight="bold")
    f.text(0.04, 0.815, "İşlem başına 1R risk, maliyet dahil, aynı anda model × enstrüman başına tek işlem · "
           "kümülatif net R (havuz)", fontsize=8, color=INK2)
    ax = f.add_axes([0.08, 0.14, 0.74, 0.6], facecolor=SURF)
    ends = []
    for model, insts, lab, col in series:
        g = tr[tr.model == model]
        if insts:
            g = g[g.inst.isin(insts)]
        g = g.sort_values("t_exit")
        eq = g.R_net.cumsum().to_numpy()
        t = pd.DatetimeIndex(g.t_exit).tz_convert(None)
        ax.plot(t, eq, color=col, lw=1.8)
        ends.append([eq[-1], eq[-1], f"{lab}  {eq[-1]:+.0f}R".replace("-", "−"), t[-1]])
    # bitiş etiketleri çakışmasın: en az 14R aralık
    ends.sort(key=lambda e: -e[0])
    for i in range(1, len(ends)):
        if ends[i - 1][1] - ends[i][1] < 14:
            ends[i][1] = ends[i - 1][1] - 14
    for v, yl, txt, tt in ends:
        ax.text(tt + pd.Timedelta(days=30), yl, txt, fontsize=7, color=INK, va="center")
    ax.axhline(0, color=INK2, lw=0.9)
    ax.grid(axis="y", color=GRID, lw=0.8)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(labelsize=7)
    ax.set_xlim(pd.Timestamp("2020-01-01"), pd.Timestamp("2026-01-01"))
    ax.set_xticks(pd.to_datetime([f"{y}-01-01" for y in range(2020, 2026)]))
    ax.set_xticklabels([str(y) for y in range(2020, 2026)])
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:+.0f}R".replace("-", "−")
                                                                 if v else "0"))
    footer(f)
    save(f, "4_backtest.png")


if __name__ == "__main__":
    cover()
    claims()
    bias()
    equity()
    print("ok")
