# Faz 0: Veri hazırlık raporu (Dreyko modeli, NQ ve ES 1dk)

Tarih: 2026-11-06 · Kod: `faz0_checks.py`, `dreyko_data.py`, testler `test_faz0_checks.py` (6/6 geçti) · Ham sonuçlar: `faz0_results.json`

**Kapsam:**
- Yalnızca IS dosyaları kullanıldı: `nq_1m_continuous_2020_2025`, `es_1m_continuous_2020_2025`. 2026 OOS dosyaları açılmadı.
- Sinyal, getiri veya performans hesabı yapılmadı. Bu belge yalnızca veri bütünlüğünü ve pencere kapsamını raporlar.

## Sonuç: Veri kullanılabilir. Bir etiket hatası bulundu ve yükleyicide düzeltildi.

| Kontrol | NQ | ES | Not |
|---|---|---|---|
| Satır / aralık | 2.118.174, 2020-01-01 18:00 – 2025-12-31 16:59 NY | 2.118.338, aynı aralık | 2026 verisi yok |
| Mükerrer zaman damgası, sıralama, NaN, High<Low, O/C aralık dışı, hacmi 0 olan bar | 0 | 0 | |
| Ayarsız fiyatların 0.25 tick ızgarasında olması | 100% | 100% | Ayarlı fiyatlar oranla çarpıldığı için ızgarada değil. Tick bazlı eşiklerde `*_unadj` kullanılmalı |
| `datetime_ny` ile `ts_utc` tutarlılığı | 0 uyumsuzluk, ofset −4/−5 sa | aynı | Yaz/kış saati geçişleri doğru |
| RTH sınırları | 09:30–15:59 | aynı | |
| **`session_date` etiketi** | **2160 satır hatalı** | **2160 satır hatalı** | Aşağıya bak |

## 1. Bulunan hata: `session_date` (DST bitiş pazarları)
- **Hata:** Kasım'ın ilk pazarındaki 18:00–23:59 NY barlarına (6 gün × 360 dk) `session_date` olarak pazartesi değil pazar yazılmış. Etkilenen günler: 2020-11-01, 2021-11-07, 2022-11-06, 2023-11-05, 2024-11-03, 2025-11-02.
- **Etkisi:** O 6 pazartesinin Asya range'i (20:00–00:00) `session_date` ile gruplanınca boş çıkıyor. Bu da A+ draw'ı, Asia Range Model'i ve önceki gün seviyelerini bozar.
- **Çözüm:** `dreyko_data.load_is()` `session_date`'i `datetime_ny`'den yeniden türetiyor (NY ≥ 18:00 ise ertesi gün). Orijinal kolon `session_date_src` olarak korunuyor. Testle doğrulandı: yalnızca bu 2160 satır değişiyor.
- **Veri dosyasına dokunulmadı.** Aynı hata diğer projelerin bu kolonu kullanan kodunu da etkileyebilir. Kullanıcıya bildirilecek; `veri notları`'ye not eklenmesi önerilir.

## 2. Bar zaman damgası semantiği
Bar etiketi açılış zamanını gösteriyor (Databento ohlcv-1m). Kanıt, dakika bazında medyan hacim:

| Dakika | NQ | ES |
|---|---|---|
| 09:29 | 779 | 2391 |
| 09:30 | 4726 | 12299 |
| 08:29 | 180 | 404 |
| 08:30 | 418 | 865 |

Açılış ve haber sıçraması kendi etiketli barında görülüyor. Yani 09:30 barı 09:30:00–09:30:59 aralığını kapsar.

Kodlama sonuçları:
- 09:30 barının bilgisi ancak 09:31:00'de kullanılabilir.
- "09:30 sonrası ilk FVG" şöyle hesaplanır: 3'lünün ilk barı en erken 09:31 olur (09:30 barının kendi FVG'si hariç). FVG, 3. bar kapanınca kesinleşir.

## 3. Pencere kapsamı (1548 RTH günü)
| Pencere (NY) | Tam gün | Eksik dakikalı gün | Not |
|---|---|---|---|
| Asya 20:00–00:00 | NQ 1492 / ES 1421 | NQ 50 / ES 121 (p95 eksik = 1 dk) | 6 "boş" gün = §1'deki etiket hatası; düzeltmeyle dolu |
| Açılış öncesi 08:00–09:30 | 1538–1540 | 8–10 | Çoğu Mart 2020 (circuit breaker / limit) ve 2025-11-28 |
| 09:30–10:00 | 1545 | 3 | 2020-03-09/12/16 (limit down), 2024-01-09, 2024-02-15 |
| Makro 09:50–10:10 | 1548 | 0 | |
| 09:30–12:10 | 1545 | 3 | |

- **FVG için ardışık 3 bar oranı:** Asya'da 99.0%, açılış öncesinde 97.7%, 09:30–12:10 arasında 98.7%. Kalan kısım işlem olmayan dakikalar; Databento işlemsiz dakikayı bar olarak yazmıyor. FVG tespiti dakika boşluklarını kontrol etmeli: ya boşluklu 3'lüler atılmalı ya da boş dakikalar doldurulmalı. Bu bir karar noktası.
- **NQ–ES hizalaması (SMT için):** 09:30–12:10 arasında NQ'nun 247.639 dakikasının tamamı ES'de de var (ES'de fazladan 1 dk). Açılış öncesinde ortak dakika 99.9%, Asya'da 99.9%.

## 4. Tatil ve yarım günler
- **RTH'siz hafta içi günler (17):** Kutsal Cuma'lar, Noel ve yılbaşı tatilleri, 2025-01-09 (Carter cenazesi). Doğru.
- **Erken kapanışlar (52):** 12:59 ya da 13:14'te biten günler. Federal tatil günlerinde CME 13:00'te kapanıyor (MLK, Presidents, Memorial, July 4, Labor, Thanksgiving, Juneteenth); arife günlerinde (Black Friday, 24 Aralık, 3 Temmuz) 13:15'te.
- **Öneri:** Tatil günlerinde 09:30 açılışı yok ama barlar var (ETH olarak etiketli). Hipotez testinde bu 52+17 gün ayrı işaretlenmeli ya da dışlanmalı. Önceden tanımlanmış bir filtre olarak dışlanmasını öneririm; bu da kullanıcı kararı.

## 5. Roll'lar
- **NQ:** 24 roll; neredeyse hepsi pazar 18:00–20:00 arasında. **ES:** 24 roll; 2022 öncesi perşembe 19:00–20:00, sonrası pazar.
- 11 NQ ve 9 ES roll'u Asya penceresine (20:00) denk geliyor. Fiyatlar oran bazlı ayarlı olduğu için seviye sıçraması yok; bu roll barlarındaki getiri 0.0x%.
- Büyük roll bar getirileri (NQ %1.5 / %1.0, ES %2.7 / %1.2; 2020 Mart ve Haziran) pazar açılışı gap'idir, yani gerçek hafta sonu hareketidir (veri notları §4 ile tutarlı).
- 09:30–12:10 penceresine denk gelen roll yok.

## 6. Ekonomik takvim doğrulaması (CPI ve NFP, IS: 143 olay)
- Takvimdeki tüm olaylar 08:30 ET'de ve hepsinde bar var.
- **08:30 barının medyan range'i:** olay günlerinde NQ %0.49 / ES %0.39; olay olmayan günlerde NQ %0.056 / ES %0.044 (yaklaşık 9 kat).
- **Hacim sıçraması:** 08:30 hacmi, önceki 10 dakikanın medyanının 15–17 katı. Olayların 89.5%'unda bu oran 3 katın üzerinde.
- Sonuç: takvim saatleri veride gerçekten olay sıçraması gösteriyor. News Model testi için kullanılabilir. Not: Takvimdeki `shock_*` / `*_spike_ratio` kolonları olay sonrası bilgi taşıyor ve feature olarak kullanılmaz.

## 7. Kodlama için çıkan kurallar (Aşama 2'ye taşınacak)
1. **Veri yükleme:** Her zaman `dreyko_data.load_is()` kullanılmalı (session_date düzeltmeli).
2. **Bilgi zamanı:** Karar anında yalnızca kapanmış barlar kullanılır; işlem sonraki barın açılışında alınır.
3. **Asya range'i:** session_date içindeki 20:00–23:59 NY barları. Pazartesi günleri pazar 18:00 açılışından sonraki barlar.
4. **Fiyat ölçeği:** FVG ve seviye karşılaştırmaları ayarlı fiyatla yapılabilir (dosya içinde tutarlı). Tick/puan cinsinden eşikler `*_unadj` ile ya da yüzde/ATR olarak tanımlanmalı.
5. **Hariç tutma:** Tatil/yarım günler ve 2020 Mart'taki limit günleri, sonuçlar görülmeden önce karara bağlanacak bir filtre adayı.
6. **Maliyet (veri notları §8):** NQ için $4 RT + taraf başına 1 tick kayma; ES için $4 RT + taraf başına 0.5 tick.
