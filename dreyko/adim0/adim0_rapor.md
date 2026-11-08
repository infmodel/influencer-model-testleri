# Dreyko — Adım 0 raporu: olay çalışması (backtest değil)

**Tarih:** 7 Kasım 2026 · **Veri:** NQ ve ES 1dk, yalnızca IS 2020–2025 (2026 OOS'a dokunulmadı) · **Kod:** `events.py`, `run_adim0.py`, `test_events.py` (10/10 test geçti, sızıntı testi dahil) · **Ham çıktılar:** `out/`

## 1. Özet

**Hiçbir olayda, hiçbir ufukta, hiçbir alt kümede bilgi bulunamadı.**

- NQ'da 7 olay × 7 alt küme × 4 ufuk = 192 testin en küçük BH-FDR q-değeri **0.996**. ES'de **0.84**. Bonferroni ile hepsi 1.0.
- Ortalama etkiler ±0.01 ATR'nin altında. NQ'da bu yaklaşık ±3 puan (medyan ATR 282 puan). İşlem maliyeti tek başına NQ'da ~0.0025 ATR, ES'de ~0.005 ATR; yani en iyimser okumada bile etkinin büyük kısmını maliyet götürür.
- Kazanma oranları %48–52, medyanlar sıfır civarında. Devam ve dönüş yönü ayırt edilemiyor.
- MFE ve MAE dağılımları neredeyse aynı (öğlene kadar medyan ~0.2 ATR lehte, ~0.2 ATR aleyhte): olaydan sonra fiyat iki yöne eşit gidiyor.
- Ağaç modeli (yıl dışarıda bırakmalı CV) olay sonrası yönü tahmin edemiyor: OOF AUC 0.49–0.55, IC −0.03…+0.07.
- Mart 2020 çıkarılınca tablo değişmiyor.

**Önerim:** Bu çekirdek tanımlarla backtest'e geçmemek (kararı sen vereceksin, §9).

## 2. Ne test edildi

Sonuçlardan önce sabitlenen tanımlar (`karar_gunlugu.md`). Yön her olayda "doğal" hipotez yönüdür; ters yön aynı sayının eksi işaretlisidir, yani iki yön de aynı testte görülüyor.

| Olay | Tanım | Doğal yön | Giriş |
|---|---|---|---|
| FPFVG_form A/B | 09:30 sonrası ilk 1dk FVG (3'lünün ilk barı ≥09:31; 3. bar A: ≤09:59, B: ≤09:44) | FVG yönü (devam) | Kesinleştiği barın kapanışından sonraki açılış |
| FPFVG_retest A/B | Aynı FPFVG'nin yakın kenarına ilk dokunuş (A: ≤11:09, B: ≤10:09) | FVG yönü | Kenarda limit (açılış kenarın ötesindeyse açılış) |
| SWEEP (H2 tetiği) | 08:00–09:29 range'inin bir ucunun 09:30–09:59 arası ilk aşılması; 09:30 açılışı range içinde olmalı | Dönüş | Sonraki açılış |
| IFVG (H2) | Sweep sonrası, sweep bacağındaki son FVG'nin (3. bar ≥09:00, uç barı dahil) ters body kapanışla kırılması, ≤11:09 | Dönüş | Sonraki açılış |
| TSCISD (H2b) | Sweep → range içine kapanış (ilk tepki) → ilk sweep ucunun yeniden aşılması (TS) → uca götüren ardışık karşı mumların ilkinin açılışı ötesinde body kapanış (CISD), ≤11:09 | Dönüş | Sonraki açılış |

- **Etiket (önceden donduruldu):** Girişten +15, +30, +60 dk ve 12:00'deki fiyat; önceki tamamlanmış günün ATR(14)'üne bölündü.
- **Koşulsuz baz (H0):** Her gün, her dakikada (09:30–11:09) açılıştan long getirinin ortalaması. "Fazla getiri" = doğal yön × (olay getirisi − aynı dakikanın bazı). Baz pratikte sıfır olduğu için fazla getiri ham getiriyle neredeyse aynı çıktı.
- **SMT:** Karar anına kadar NQ ve ES'den yalnızca birinin ilgili PM ucunu alması (long için low, short için high).
- **Makro:** Giriş barı 09:50–10:09 arasında.

## 3. Olay sıklığı (NQ, 1534 uygun gün)

| Olay | n | Günlerin %'si | SMT var | Makro içi |
|---|---|---|---|---|
| FPFVG_form_A | 1529 | %99.7 | %22 | %2 |
| FPFVG_form_B | 1435 | %93.5 | %22 | %0 |
| FPFVG_retest_A | 1373 | %89.5 | %22 | %11 |
| FPFVG_retest_B | 1220 | %79.5 | %23 | %9 |
| SWEEP | 1432 | %93.4 | %54 | %2 |
| IFVG | 1432 | %93.4 | %31 | %18 |
| TSCISD | 839 | %54.7 | %18 | %35 |

**Önemli gözlem:** Mekanik tanımlarla bu olaylar neredeyse **her gün** oluşuyor.
- FPFVG genelde 09:34–09:36'da çıkıyor ve küçük (medyan 0.018 ATR ≈ 5 NQ puanı).
- 08:00–09:30 range'i (medyan 0.20 ATR) 10:00'dan önce %93 ihtimalle süpürülüyor.
- Dreyko "her gün manipülasyon aranmaz" diyor. Onun seçiciliği bu kurallarda değil, kodlanmayan HTF "key level / bias" katmanında (§8).

## 4. Ana sonuçlar (tüm olaylar, ATR birimi, doğal yönde)

| Olay | NQ 60dk ort. (t) | NQ 12:00 ort. (t) | NQ isabet 12:00 | ES 60dk ort. (t) | ES 12:00 ort. (t) |
|---|---|---|---|---|---|
| FPFVG_form_A | +0.007 (0.97) | +0.006 (0.63) | %51.3 | −0.001 (−0.10) | −0.007 (−0.71) |
| FPFVG_form_B | +0.004 (0.55) | +0.001 (0.11) | %50.9 | −0.001 (−0.18) | −0.009 (−0.90) |
| FPFVG_retest_A | +0.010 (1.35) | +0.007 (0.65) | %50.3 | −0.000 (−0.04) | −0.008 (−0.78) |
| FPFVG_retest_B | +0.008 (0.95) | +0.003 (0.23) | %50.0 | −0.002 (−0.27) | −0.012 (−1.11) |
| SWEEP | −0.002 (−0.27) | −0.003 (−0.29) | %49.0 | +0.006 (0.79) | +0.003 (0.29) |
| IFVG | +0.002 (0.27) | +0.003 (0.29) | %49.0 | +0.006 (0.87) | +0.002 (0.20) |
| TSCISD | −0.009 (−1.10) | +0.005 (0.47) | %48.7 | −0.004 (−0.47) | −0.007 (−0.61) |

- Hiçbir |t| 1.4'ü geçmiyor.
- Yıl istikrarı: 6 yılın en fazla 4'ünde aynı işaret, yani yazı-tura düzeyi.
- NQ ve ES işaretleri birbirini tutmuyor; örneğin FPFVG NQ'da hafif pozitif, ES'de hafif negatif.

## 5. Alt kümeler (SMT, makro, long/short)

Ham p < 0.05 çıkan hücreler (192 test içinde şans eseri ~10 tane beklenir):
- NQ FPFVG_form_A, makro içi (n=33): 12:00'de +0.136 ATR, p=0.013, q=0.996. Bunlar 09:49–09:59 arasında geç oluşan FPFVG'ler; örneklem çok küçük.
- NQ IFVG short, 15dk: +0.012 ATR, p=0.043, q=0.996.
- ES TSCISD makro dışı, 30dk: −0.017, p=0.024. ES IFVG makro içi, 15dk: −0.016, p=0.037. İkisi de q=0.84.

**SMT** tutarlı bir katkı yapmıyor:
- NQ'da IFVG ve TSCISD için SMT'li alt küme **daha kötü** (−0.005, −0.031).
- ES'de aynı alt kümeler daha iyi (+0.037, +0.048).
- Bu zıtlık gürültüyle uyumlu.

Post-hoc not (ön kayıtlı değil, test sayısına eklenmedi): SMT **ve** makro birlikte (n=8–59), ES'de tüm olaylarda pozitif (+0.01…+0.11). NQ'da karışık (SWEEP −0.13, IFVG −0.02). Örneklem küçük ve iki enstrüman çelişiyor; kanıt sayılmaz.

## 6. MFE / MAE (öğlene kadar, ATR, NQ)

| Olay | MFE medyan | MAE medyan | MFE %75 | MAE %75 |
|---|---|---|---|---|
| FPFVG_form_A | 0.230 | 0.210 | 0.396 | 0.401 |
| FPFVG_retest_A | 0.211 | 0.202 | 0.384 | 0.385 |
| SWEEP | 0.223 | 0.235 | 0.409 | 0.402 |
| IFVG | 0.201 | 0.208 | 0.391 | 0.366 |
| TSCISD | 0.177 | 0.185 | 0.315 | 0.313 |

Lehte ve aleyhte gidiş simetrik. Bu, stop ve hedef ayarlarıyla "kâr çıkarılabilecek" bir asimetri olmadığı anlamına geliyor. Sabit R ya da likidite hedefli bir backtest, maliyet öncesi beklentisi yaklaşık sıfır olan bir dağılımı yeniden paketlemiş olur.

## 7. Öznitelikler (NQ)

- **Tek öznitelik IC'leri** (Spearman, 12:00 getirisi; 64 test): En güçlüsü IFVG'de sweep derinliği (IC −0.072, p=0.006, q=0.41). Hiçbiri FDR'den geçmiyor.
- **Ağaç modeli + permutation importance** (HistGradientBoosting, leave-one-year-out): OOF AUC FPFVG_form_B'de 0.545, diğerlerinde 0.49–0.53.
  - En tutarlı katkıyı bir önceki günün getirisi (`prev_ret_atr`, 6/6 katta pozitif) ve PM range genişliği veriyor.
  - Bunlar genel rejim değişkenleri; Dreyko'nun mekanizmasına özgü değiller ve etki boyutu küçük (MDA ≈ 0.02 AUC).

## 8. Sınırlamalar: test edilmeyenler

- **HTF bias ve "key level":** 4sa/günlük FVG, OB, haftalık range, COT. Dreyko'nun "3 şart"ının ilki ve seçiciliğin ana kaynağı bu katman, ama videolarda sübjektif tanımlanıyor. Sonucumuz "Dreyko'nun takdiri değersiz" demiyor. Söylediği şu: **kodlanabilen gün içi tetikler (FPFVG, sweep, IFVG, TS+CISD, SMT, makro) tek başına bilgi taşımıyor.**
- **"09:30 öncesi likidite" ön koşulu:** Equal high/low ve LRLR kodlanmadı. PM range uçları vekil olarak kullanıldı.
- **Takdirî çıkışlar:** Haber anına pozisyon taşımak ve SMT ile erken çıkmak etiketlerde yok. Etiketler sabit ufuklu.
- **Fiyat serisi:** Fiyatlar ratio-adjusted seriden (oranlar korunur). Limit dolumlarının bazı bar açılışından ölçülüyor; küçük bir uyumsuzluk var ama baz zaten ≈0.
- **Spot kontrol:** Kodun tanımları Dreyko'nun 4 Haziran 2025 ES canlı işlemiyle örtüşüyor. O gün aynı yönde bearish FPFVG yakalandı (09:44, 5994.5–5996.75; videoda 5993.75–5996.50). 10:00 mumunun dibi videodakiyle aynı (5983.50). O gün olay kârlı; sorun tanımda değil, 1500 günün ortalamasında.

## 9. Çoklu test kaydı

| Aile | NQ | ES |
|---|---|---|
| Olay × alt küme × ufuk (ham) | 192 | 192 |
| Aynı, koşulsuz baza göre fazla getiri | 192 | 192 |
| Tek öznitelik IC | 64 | 64 |
| Ağaç modeli (LOYO) | 7 model | — |

Toplam 896 p-değeri ve 7 model. `karar_gunlugu.md` dosyasına işlendi.

## 10. Karar seçenekleri (kullanıcı)

1. **NO-GO, arşivle (önerim).** Çekirdek gün içi model Adım 0'da eleniyor. Çıkarımlar arşive yazılır; backtest çalıştırılmaz.
2. **Seçicilik katmanını mekanikleştirip yeni ön-kayıtlı tur.** Örnek: "09:30 öncesi fiyat önceki gün H/L'sine ya da Asya H/L'sine dokunmuş olmalı" (taslaktaki ön koşul (b)). Bu yeni bir hipotezdir ve deneme sayacını artırır. Bu raporu gördükten sonra seçilen her filtre post-hoc risk taşır; filtre ekonomik gerekçeyle, sonuca bakmadan seçilmeli.
3. **Yine de backtest.** Metodolojiye göre Adım 0'da bilgi taşımayan sinyal backtest'e girmez. Bu seçenek seçilirse karar günlüğüne sapma olarak yazılır.
