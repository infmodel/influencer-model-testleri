"""Twitter paylaşımı için 4 görsel (1600x900). Veri: adim0/out ve backtest/out (IS 2020-2025)."""
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
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
CRIT = "#d03b3b"
plt.rcParams.update({"font.family": ["Noto Sans", "DejaVu Sans"], "text.color": INK, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": GRID})
W, H, DPI = 8, 4.5, 200
FOOT = "Veri: CME NQ & ES 1 dk, 2020–2025 · Yalnızca YouTube serisinde anlatılan kurallar test edildi"


def fig():
    f = plt.figure(figsize=(W, H), dpi=DPI, facecolor=SURF)
    return f


def footer(f, extra=None):
    f.text(0.04, 0.035, FOOT if extra is None else extra, fontsize=6.5, color=MUTED)


def save(f, name):
    f.savefig(OUT / name, facecolor=SURF, dpi=DPI)
    plt.close(f)


# ------------------------------------------------------------- 1. kapak
def cover():
    f = fig()
    f.text(0.04, 0.88, "Dreyko'nun YouTube'da anlattığı trade modelini", fontsize=17, weight="bold")
    f.text(0.04, 0.80, "6 yıllık gerçek veride test ettik.", fontsize=17, weight="bold")
    f.text(0.04, 0.715, "Sonuç: Videolardaki kurallarla sistematik bir avantaj yok. Maliyetler düşülünce zarar.",
           fontsize=9.5, color=INK2)
    tiles = [("1.534", "işlem günü\n(NQ ve ES, 2020–2025)"),
             ("0 / 32", "backtest varyantından\nbaşarı şartını geçen"),
             ("0", "çoklu test düzeltmesinden\nsonra anlamlı sonuç\n(1.200+ istatistik testi)")]
    x0, w, gap = 0.04, 0.287, 0.0245
    for i, (big, small) in enumerate(tiles):
        x = x0 + i * (w + gap)
        f.patches.append(FancyBboxPatch((x, 0.28), w, 0.34, boxstyle="round,pad=0,rounding_size=0.015",
                                        transform=f.transFigure, facecolor="#f0efec", edgecolor="none"))
        f.text(x + 0.025, 0.465, big, fontsize=30, weight="bold", color=CRIT if i else INK)
        f.text(x + 0.025, 0.42, small, fontsize=8.5, color=INK2, va="top", linespacing=1.35)
    footer(f)
    save(f, "1_sonuc.png")


# ------------------------------------------------------------- 2. yöntem
def method():
    f = fig()
    f.text(0.04, 0.89, "Nasıl test ettik?", fontsize=17, weight="bold")
    f.text(0.04, 0.815, "Kurallar videolardan çıkarıldı, koda döküldü ve sonuçlara bakılmadan kilitlendi.",
           fontsize=9, color=INK2)
    steps = [("1", "67 videonun\ntranskripti tarandı", "Model anlatılan videolar\nayıklandı"),
             ("2", "11 kilit video\nyapay zekâya izletildi", "Saatler, giriş, stop,\nhedef netleştirildi"),
             ("3", "Kurallar\nkoda döküldü", "FPFVG, sweep, IFVG,\nTurtle Soup + CISD, SMT"),
             ("4", "Kod doğrulandı", "4 Haziran 2025 canlı\nişlemini aynen yakaladı")]
    w, gap, y = 0.21, 0.0233, 0.47
    for i, (n, a, b) in enumerate(steps):
        x = 0.04 + i * (w + gap)
        f.patches.append(FancyBboxPatch((x, y), w, 0.27, boxstyle="round,pad=0,rounding_size=0.015",
                                        transform=f.transFigure, facecolor="#f0efec", edgecolor="none"))
        f.text(x + 0.018, y + 0.205, n, fontsize=11, weight="bold", color=S1)
        f.text(x + 0.05, y + 0.235, a, fontsize=8.0, weight="bold", va="top", linespacing=1.25)
        f.text(x + 0.018, y + 0.03, b, fontsize=7.2, color=INK2, va="bottom", linespacing=1.3)
    f.text(0.04, 0.39, "Sonra üç ayrı sınav:", fontsize=10, weight="bold")
    exams = [("Olay çalışması", "Kurulumdan sonra fiyat\nnereye gidiyor?", "Belirgin yön yok"),
             ("Kendi filtreleri", "A+ seviye süpürmesi,\naçık hedef, \"3 şart\"", "Anlamlı fark yok"),
             ("Backtest", "32 varyant, stop/hedef,\nkomisyon ve kayma dahil", "Hiçbiri geçmedi")]
    w2, gap2 = 0.287, 0.0245
    for i, (a, b, r) in enumerate(exams):
        x = 0.04 + i * (w2 + gap2)
        f.patches.append(FancyBboxPatch((x, 0.1), w2, 0.25, boxstyle="round,pad=0,rounding_size=0.015",
                                        transform=f.transFigure, facecolor=SURF, edgecolor=GRID, linewidth=1))
        f.text(x + 0.02, 0.305, a, fontsize=9, weight="bold", va="top")
        f.text(x + 0.02, 0.255, b, fontsize=7.2, color=INK2, va="top", linespacing=1.3)
        f.text(x + 0.02, 0.125, "✗  " + r, fontsize=8.5, weight="bold", color=CRIT)
    footer(f)
    save(f, "2_yontem.png")


# ------------------------------------------------------------- 3. olay çalışması
def events():
    keys = [("FPFVG_form_A", "İlk FVG (FPFVG) oluşur"), ("FPFVG_retest_A", "Fiyat FPFVG'ye geri döner"),
            ("SWEEP", "Açılışta range ucu süpürülür"), ("IFVG", "IFVG ile dönüş"),
            ("TSCISD", "Turtle Soup + CISD")]
    ev = pd.read_parquet(ROOT / "adim0/out/events_NQ.parquet")
    n_days = 1534
    rate = ev.groupby("key").size() / n_days
    f = fig()
    f.text(0.04, 0.89, "Kurulumdan sonra fiyat iki yöne eşit gidiyor", fontsize=16, weight="bold")
    f.text(0.04, 0.815, "Kurulum anından öğlene (12:00 NY) kadar ortalama getiri, %95 güven aralığı · "
           "birim: günlük oynaklık (ATR)", fontsize=8.5, color=INK2)
    ax = f.add_axes([0.37, 0.17, 0.58, 0.58], facecolor=SURF)
    ys = np.arange(len(keys))[::-1]
    for sym, col, off in (("NQ", S1, 0.13), ("ES", S2, -0.13)):
        s = pd.read_csv(ROOT / f"adim0/out/stats_{sym}.csv")
        s = s[(s.subset == "tümü") & (s.horizon == "noon")].set_index("key")
        for y, (k, _) in zip(ys, keys):
            m, t = s.at[k, "mean"], s.at[k, "t"]
            se = abs(m / t)
            ax.plot([m - 1.96 * se, m + 1.96 * se], [y + off] * 2, color=col, lw=2, solid_capstyle="round")
            ax.plot(m, y + off, "o", ms=6.5, color=col, mec=SURF, mew=1.5, zorder=3)
    ax.axvline(0, color=INK2, lw=1)
    ax.set_xlim(-0.06, 0.06)
    ax.set_xticks([-0.05, -0.025, 0, 0.025, 0.05])
    ax.set_xticklabels(["−0.05", "−0.025", "0", "+0.025", "+0.05"], fontsize=7)
    ax.set_yticks([])
    ax.grid(axis="x", color=GRID, lw=0.8)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.set_ylim(-0.6, len(keys) - 0.4)
    for y, (k, lab) in zip(ys, keys):
        f.text(0.04, 0.17 + 0.58 * (y + 0.6) / len(keys), lab, fontsize=8.2, va="center",
               transform=f.transFigure)
        f.text(0.30, 0.17 + 0.58 * (y + 0.6) / len(keys), f"%{rate[k] * 100:.1f}", fontsize=8, va="center",
               color=INK2, ha="right", transform=f.transFigure)
    f.text(0.30, 0.765, "görüldüğü günler", fontsize=6.5, color=MUTED, ha="right")
    ax.text(-0.058, len(keys) - 0.45, "● NQ", color=S1, fontsize=7.5, va="top")
    ax.text(-0.04, len(keys) - 0.45, "● ES", color=S2, fontsize=7.5, va="top")
    ax.text(0.059, -0.55, "Tüm aralıklar sıfırı kesiyor = avantaj yok", fontsize=6.8, color=MUTED, ha="right")
    footer(f, FOOT + " · kurulum başına 800–1.500 olay")
    save(f, "3_olay_calismasi.png")


# ------------------------------------------------------------- 4. backtest equity
def equity():
    tr = pd.read_parquet(ROOT / "backtest/out/trades_NQ.parquet")
    hyps = [("H1-A", "İlk FVG (FPFVG)", S1), ("H2", "Sweep + IFVG", S2), ("H2b", "Turtle Soup + CISD", S3)]
    f = fig()
    f.text(0.04, 0.89, "Backtest: 6 temel kuralın 6'sı da 6 yıl sonunda zararda", fontsize=16, weight="bold")
    f.text(0.04, 0.815, "NQ, 1 kontrat, komisyon + kayma dahil, aynı mumda stop ve hedef görülürse stop sayıldı "
           "· kümülatif net $", fontsize=8.5, color=INK2)
    titles = {"L": "Hedef: açılış öncesi range'in karşı ucu", "R": "Hedef: 2R (riskin 2 katı)"}
    for i, tg in enumerate(("L", "R")):
        ax = f.add_axes([0.08 + i * 0.47, 0.13, 0.36, 0.52], facecolor=SURF)
        ax.set_title(titles[tg], fontsize=8.5, loc="left", color=INK, pad=6)
        for h, lab, col in hyps:
            g = tr[(tr.hyp == h) & (tr.target == tg)].sort_values("date")
            eq = g.usd.cumsum() / 1000
            ax.plot(g.date, eq, color=col, lw=1.6)
            ax.text(g.date.iloc[-1] + pd.Timedelta(days=40), eq.iloc[-1], ("−" if eq.iloc[-1] < 0 else "+") + f"${abs(eq.iloc[-1]):.0f}K",
                    fontsize=7, color=INK, va="center")
        ax.axhline(0, color=INK2, lw=0.9)
        ax.set_ylim(-88, 48)
        ax.grid(axis="y", color=GRID, lw=0.8)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(labelsize=7)
        ax.set_xlim(pd.Timestamp("2020-01-01"), pd.Timestamp("2026-07-01"))
        ax.set_xticks(pd.to_datetime([f"{y}-01-01" for y in range(2020, 2026)]))
        ax.set_xticklabels([str(y) for y in range(2020, 2026)])
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: ("−" if v < 0 else "") + f"${abs(v):.0f}K"))
    x = 0.07
    for h, lab, col in hyps:
        f.text(x, 0.755, "━ ", color=col, fontsize=9, weight="bold")
        f.text(x + 0.025, 0.755, lab, fontsize=8, color=INK)
        x += 0.03 + len(lab) * 0.0105
    footer(f)
    save(f, "4_backtest.png")


if __name__ == "__main__":
    cover()
    method()
    events()
    equity()
    print("ok")
