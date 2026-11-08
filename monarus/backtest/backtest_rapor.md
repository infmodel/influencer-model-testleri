# Backtest raporu: Monarus modelleri (iddia testi, sapma)

Tarih: 2026-11-08 · Ön kayıt: `on_kayit_bt.md` (sonuçlardan önce) · Kod: `bt.py`, `run_bt.py` · Testler: `test_monarus_bt.py` (8/8) + `adim0/test_monarus_adim0.py` (23/23) · Çıktılar: `out/summary.csv` (260 satır), `out/trades.parquet` (58.471 işlem), `out/monthly.csv`, `out/claims.json`, `out/meta.json`

**Bu bir sapmadır:** Adım 0'da hiçbir sinyal geçmedi. Backtest kullanıcının isteğiyle, **iddiaları sınamak için** yapıldı; sistem seçmek için değil.
- Kurallar Adım 0'daki 23 tanımın birebir aynısı (+ MC BE varyantı). Sonuca bakılarak hiçbir şey değiştirilmedi.
- Kurulum: IS 2020–2025, işlem başına 1R, model × enstrüman başına aynı anda tek pozisyon, SL-first, maliyet dahil (data/CLAUDE.md; AUD/JPY spot geçici 1,3 pip).

## Sonuç: Videolarda öğretilen kuralların hiçbiri bu veride kârlı değil. İddia edilen kazanç oranları kuralların kendisiyle üretilemiyor.

- **Kârlılık:** Ön kayıtlı "kurallar kârlı" barajını 260 satırın (225 tekil anahtar + 35 havuz) **hiçbiri** geçmiyor.
  - Maliyet sonrası ortalaması pozitif olan 39 tekil anahtar var. Hepsi küçük örneklemli tek parite/varyant hücreleri; hiçbirinde DSR > 0,16 yok.
  - Model başına havuzlarda tek istisna MD-1G-b: 6 yılda 7 enstrümanda 18 işlem, +0,08R, perm. p = 0,33, DSR 0,22. Geri kalan tüm havuzlar negatif.
- **İddia kıyası:**

| İddia | Kaynak | Ölçülen (bu kurallarla, 2020–2025) |
|---|---|---|
| MB: "%75 win rate'in hiç altına düşmedim", en yüksek %88 (5–6 aylık testler) | Sk5 [01:09] | WR **%47,4** (%95 GA %44–51), 3 paritede 927 işlem. 6 aylık pencerelerin en kötüsü %32, en iyisi %61. Pencerelerin hiçbirinde %75 yok |
| MB: "17 işlem, 15 TP" (%88,24) | Sk5 [27:15] | 17 ardışık işlemlik pencerelerde en yüksek WR %76,5 (13/17). %88'e **hiç** ulaşılmıyor |
| MF: WR "%68–80", filtreyle "%80–85" | 97GD [15:59] | WR **%57,5** (%55–60). Başabaş %57,2. 6 aylık pencerelerin en iyisi %69 |
| MD: "win rate'im %75", "ayda 6–10R" | U8, pchmm [09:19] | 1,8R kuralıyla 7 enstrümanda 6 yılda **15 işlem** (4S) / 24 (1G); WR %27–29. RR filtresiz WR %68 ama RR 0,41 (başabaş %70). **Aylık R medyanı −0,29; 6R ve üstü ay: 0** |
| MA: bias isabeti %60–80 | Uzd [26:20] | Rakam çıkıyor (%64–68), ama aynı mesafede ters seviye de aynı oranda (Adım 0 §1). İşlem katmanı MA-T: WR %12,7, ort. −0,05R |
| MC: aylık "5 TP 1 stop" vb. (~%74) | Y4 (2026, OOS, bakılmadı) | IS'te WR %25–32 (1,5R, başabaş %40). 6 aylık pencerelerin en iyisi %50 |

## 1. Model havuzları (NY17, maliyet sonrası)

| Model | İşlem | Yılda | WR (%95 GA) | Başabaş | Ort. R net | Toplam R | Ayda R | Kârlı yıl | Max DD (R) | MC DD %95 | Perm. p | DSR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MA-T | 1.348 | 225 | %12,7 (11–15) | %25,8 | −0,045 | −60 | −0,8 | 3/6 | 96 | 118 | 0,11 | 0,00 |
| ME-1 | 2.165 | 361 | %28,3 (27–30) | %37,6 | −0,118 | −256 | −3,6 | 0/6 | 281 | 289 | 0,31 | 0,00 |
| ME-1n (bias'sız) | 4.971 | 829 | %19,5 | %30,2 | −0,110 | −549 | −7,6 | 1/6 | 600 | 598 | 0,09 | 0,00 |
| ME-2 | 764 | 127 | %27,5 (24–31) | %36,9 | −0,014 | −11 | −0,1 | 2/6 | 34 | 74 | 0,31 | 0,00 |
| MF-1 | 1.582 | 264 | %57,5 (55–60) | %57,2 | −0,105 | −166 | −2,3 | 1/6 | 166 | 203 | 0,40 | 0,00 |
| MF-1k | 3.410 | 568 | %57,9 | %57,8 | −0,096 | −326 | −4,5 | 1/6 | 332 | 402 | 0,18 | 0,00 |
| MF-n (bias'sız) | 6.691 | 1.115 | %58,1 | %58,3 | −0,116 | −775 | −10,8 | 0/6 | 780 | 839 | 0,53 | 0,00 |
| MB-v (3 parite) | 927 | 155 | %47,4 (44–51) | %50 | −0,172 | −160 | −2,2 | 0/6 | 166 | 172 | 0,94 | 0,00 |
| MB-v (6 parite) | 2.221 | 370 | %49,1 | %50 | −0,147 | −326 | −4,5 | 0/6 | 336 | 341 | 0,79 | 0,00 |
| MB-h0 (filtresiz) | 5.743 | 957 | %50,0 | %50 | −0,181 | −1.037 | −14,4 | 0/6 | 1.046 | 1.049 | 0,39 | 0,00 |
| MD-4S-a (1,8R) | 15 | 2,5 | %26,7 | %30,5 | −0,329 | −5 | −0,07 | 1/5 | 7 | 11 | 0,82 | 0,07 |
| MD-1G-a (1,8R) | 24 | 4 | %29,2 | %28,5 | −0,124 | −3 | −0,04 | 2/6 | 6 | 12 | 0,37 | 0,08 |
| MD-4S-a-n1 | 388 | 65 | %68,0 (63–73) | %69,7 | −0,088 | −34 | −0,5 | 1/6 | 40 | 45 | 0,85 | 0,00 |
| MD-n0-a (POI'siz) | 454 | 76 | %29,1 | %26,9 | −0,055 | −25 | −0,3 | 2/6 | 63 | 86 | 0,09 | 0,00 |
| MC-A %1 (NQ) | 520 | 87 | %24,8 | %40 | −0,034 | −18 | −0,25 | 3/6 | 30 | 48 | 0,62 | 0,00 |
| MC-A %1 BE | 520 | 87 | %22,7 | %40 | −0,019 | −10 | −0,14 | 3/6 | 22 | 41 | 0,45 | 0,00 |
| MC-B %1 | 176 | 29 | %32,4 | %40 | −0,166 | −29 | −0,41 | 1/6 | 38 | 43 | 0,92 | 0,00 |

Ana enstrüman GBPUSD'de de tablo aynı:
- MB-v: −0,19R, WR %46,3.
- MF-1: −0,12R.
- ME-1: −0,06R.
- MD-4S-a: 6 yılda 1 işlem.
- MA-T: −0,12R.

Hiçbir model hiçbir gün sınırında (NY17 / TR 00:00) pozitif bir havuz vermiyor. Tüm satırlar `out/summary.csv` dosyasında.

**Okuma notları:**
- **Yüksek WR ama negatif sonuç:** MF ve MD-n1'in %57–68'lik kazanç oranları, RR 1'in altında (0,4–0,8) olduğu için başabaş noktasının hemen altında kalıyor. Yüksek WR burada bir avantaj değil, küçük hedefin mekanik sonucu.
- **Bias filtreleri:** Bias'lı varyantlar bias'sız negatif kontrollerle aynı sonucu veriyor (ME-1 ≈ ME-1n, MF-1 ≈ MF-n). "Günlük/haftalık bias" katmanı ölçülebilir bir şey eklemiyor.
- **Maliyet:**
  - MB'de maliyet 1R'lik hedefin ~%10'u.
  - Maliyetsiz (0×) bile havuzlar sıfır civarında: MB-v 3 parite −0,05R, ME-1 −0,01R, MF-1 +0,02R, MA-T +0,03R. 35 havuzun 33'ünde başabaş maliyet varsayılan maliyetin altında; istisnalar 18 işlemlik MD-1G-b'nin iki gün sınırı.
  - Maliyet varsayımını değiştirmek sonucu çevirmez.
- **Rastgele giriş:** Aynı gün, pencere, stop ve RR ile rastgele dakika ve yönde girilen işlemler (200 tekrar) bu kurallar kadar iyi ya da daha iyi (perm. p 0,09–0,94).
- **En iyi tekil hücreler:** ME-2 XAUUSD +0,28R (n = 101, p = 0,10, DSR 0,13), MD-n0-a USDCAD +0,22R (n = 67).
  - 225 hücrenin içinde şans eseri beklenecek düzeyde. Hiçbiri DSR'den geçmiyor.
  - Post-hoc seçim olacağı için aday da sayılmaz.

## 2. İddia edilen rakamlar nereden gelebilir? (yorum, kanıt değil)
- **Kısa ve seçilmiş pencereler:** MB-v'de 6 aylık pencerelerin %2–3'ünde tek bir parite WR %75–80'e çıkabiliyor (GBPUSD en iyi pencere %78,6, USDJPY %80). 6 yılda bu kadar kısa dönemler doğal dalgalanmayla oluşuyor. Üç paritenin havuzunda ise hiç oluşmuyor.
  - Monarus'un örnek ayı (Aralık 2025, AUDUSD): videoda 11 işlem, 10 TP. Bizde aynı ay 8 işlem, 6 TP (%75). Kendi bulduğumuz ay da ortalamanın üstünde, ama aynı kurallar 6 yıla yayılınca WR %47.
- **Sayım dışı bırakma:** Videoda sayım dışı bırakıldığı söylenen işlemler (Gemini notları, Sk5): 18:00 sonrası, 10 mumdan geç temaslar, büyük FVG ya da stop. Bunlar sonuç görüldükten sonra yapılırsa WR'yi yapay olarak yükseltir.
  - Biz bu kuralları önceden ve tutarlı uyguladık (10 mum, 08–18, 20 pip).
- **Maliyet:** İddiaların hiçbirinde maliyet yok. Bizde maliyetsiz sonuçlar da sıfır civarında; tek başına açıklama değil.
- **Kural esnekliği:** MD'nin "%20 inisiyatif"i ve açıklanmayan kuralları test edilemez. Kodlanabilir haliyle 1,8R şartı neredeyse hiç işlem üretmiyor, oysa iddia ayda 6–10R.

## 3. Kapsam (test edilmeyenler; iddiayı kurtaran yol değildir)
- Adım 0 raporu §5'teki liste: MB FVG filtresi, MF 2. deneme, MD inisiyatif / haber, MC konsolidasyon, ME Key Level.
- Monarus'un veri kaynağı (FXCM/OANDA) ve kendi göstergeleri (Daily Bias, Market Structure (5), VWMA) birebir değil. Gün ve 4S sınırı iki tanımla denendi, sonuç değişmedi.
- 2026 (kilitli OOS) kullanılmadı. MC'nin ve MB'nin 2026'daki iddia sayımları kontrol edilmedi.
- İspat yükü iddia sahibinde: videolarda anlatılanlar test edildi.

## 4. Doğrulama
- **Testler:** `test_monarus_bt.py` 8/8 geçti: sıralı işlemde çakışma atlanıyor, BE, SL-first ve boşluk, Wilson aralığı, drawdown, DSR, başabaş maliyet, kayan pencereler. Adım 0'daki 23 test de olay tanımları için geçerli.
- **Olay tanımları Adım 0 ile aynı:** İşlem sayıları da tutarlı; sıralı filtre birkaç çakışan işlemi düşürüyor (ör. MB-v 2.229 → 2.221).
- **DSR:** Sharpe varyansı ilk koşuda n < 30 anahtarların uç değerleriyle şişti (23,9). Yalnız n ≥ 30 anahtarlardan hesaplanacak şekilde düzeltildi (0,0064).
  - Hiçbir satırın sonucu bu yüzden değişmedi: baraj iki koşuda da 0 satır.

- **NQ maliyet ölçeği (bilinen küçük hata, model lehine):** MC'de maliyet gerçek fiyatla (0,7 puan), risk ise oran-ayarlı seriyle hesaplandı. Ayar katsayısı 2020'de ~1,16, 2025'te ~1,0; maliyet R'si en fazla ~%16 düşük, yani işlem başına ≤0,003R. Sonuç (MC negatif) değişmez.

## 5. Deneme sayacı (backtest)
- **260 satır** (225 tekil anahtar + 35 havuz). Her birinde 1 permütasyon testi (200 tekrar) ve 1 DSR (N = 225).
- Adım 0'daki 2.233 test ayrı sayılır.
- Koşu sayısı 2: ikincisi yalnız DSR varyans düzeltmesi.
