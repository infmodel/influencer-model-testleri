# Faz 0: Veri hazırlık raporu (Monarus, MA–MF)

Tarih: 2026-11-08 · Kod: `monarus_data.py` (yükleyici + yeniden örnekleme), `faz0_checks.py`; testler `test_monarus_faz0.py` (22/22 geçti) · Ham sonuçlar: `faz0_results.json`

**Kapsam:**
- Yalnızca IS verisi (2020-01-01 – 2025-12-31 UTC) kullanıldı. 2026 satırları yükleyicide kesiliyor; `_guard` 2026'ya ait bir satır görürse hata veriyor. OOS dosyaları açılmadı.
- Sinyal sonucu, işlem etiketi ya da performans hesaplanmadı.
- Vekil kontrolünde yalnızca özniteliklerin (günlük durum sınıfı, marubozu sıklığı) spot ile vadelide aynı çıkıp çıkmadığına bakıldı.

## Sonuç: Veri kullanılabilir. §7'deki iki soru kullanıcı tarafından karara bağlandı (8 Kasım)
- **Gün sınırı:** Ana test NY 17:00 (gün ve 4S bloklar), TR 00:00 sağlamlık testi.
- **MB enstrümanları:** GBPUSD spot ana; EURUSD, USDCAD ve USDCHF spot genelleme testi.
- **AUDUSD ve USDJPY spot verisi indirildi ve `data/`'ya eklendi:** Kaynak Dukascopy 1dk bid, diğer 4 pariteyle aynı (§9). Bütünlük kontrolleri temiz. Bu iki parite MA–MF'nin hepsinde spot olarak kullanılacak; 6A ve 6J yalnızca çapraz kontrol için kalacak.

| Kontrol | Spot (EUR, GBP, CAD, CHF, AUD, JPY) | Vadeli (6A→AUDUSD, 6J→USDJPY, GC→XAUUSD) |
|---|---|---|
| Satır | ~2,25 M / parite | 2,07 M / 2,08 M / 2,11 M |
| Mükerrer zaman damgası, sıralama, NaN, ≤0 fiyat, High<Low, O/C aralık dışı | 0 | 0 (hacmi 0 olan bar da yok) |
| Fiyat hassasiyeti | 5 hane (JPY 3 hane) (%100) | Tick ızgarasında (%100): 6A 0,00005 (0,5 pip), 6J 0,0000005, GC 0,1 |
| 15dk / 30dk bar doluluğu (TR 08–18) | %100 | 6A/6J %90 / %85 tam, %96–97'si ≥%90 dolu; GC %97. İşlem olmayan dakika bar olarak yazılmıyor |
| Roll | yok | Her birinde IS'te 24 roll (GC 30). Ayarlı seride roll barındaki sıçrama 0 (ayarsız: 6A medyan 8 pip, 6J 137 pip, GC $18) |

## 1. Bar zaman damgası: etiket = AÇILIŞ
Haber dakikasıyla etiketli 1dk barın range'i (medyan, pip):

| | NFP: dk −1 / 0 / +1 | CPI | FOMC |
|---|---|---|---|
| EURUSD spot | 3,1 / **29,1** / 10,5 | 2,7 / **30,4** / 8,8 | 2,5 / **26,4** / 13,1 |
| GBPUSD spot | 4,6 / **34,0** / 11,9 | 4,3 / **33,8** / 9,5 | 3,4 / **26,9** / 13,7 |
| AUDUSD (6A) | 3,0 / **24,4** / 8,6 | 2,5 / **25,8** / 7,2 | 2,3 / **23,6** / 10,3 |
| 6E | 4,1 / **34,5** / 12,2 | 3,3 / **32,9** / 9,7 | 3,1 / **32,8** / 15,3 |

Sıçrama kendi etiketli barında görülüyor. Takvim saatleri de doğru (NFP/CPI 08:30 NY, FOMC 14:00 NY). Sonuç: 08:30 barının bilgisi 08:31:00'de kullanılabilir. N dakikalık barlar `t_last + 1dk` anında kesinleşir; sinyal bar kapanışında, işlem sonraki barın açılışında.

## 2. Gün ve blok yapısı
- **TR 00:00 (= 21:00 UTC, sabit):** Hafta içi 5 gün oluşuyor, Pazar günü oluşmuyor. Pazar açılışı TR'de Pazartesi'ye düşüyor. Kışın Cuma kapanışından 1 saatlik bir Cumartesi artığı kalıyor (yılda ~1.070 dk, 21:00–22:00 UTC); yükleyici bunu Cuma'ya katıyor.
- **NY 17:00 (DST'li):** Artık yok. CME FX ve GC'nin günlük molası (17:00–18:00 ET) ile birebir örtüşüyor.
- **4S bloklar:** TR modunda bloklar TR 00/04/08/12/16/20'de başlıyor. NY17 modunda NY 17/21/01/05/09/13'te başlıyor; bu yazın TR 00/04/08…, kışın TR 01/05/09…'a denk geliyor.
- **Hafta:** Pazartesi işlem günüyle başlıyor; 314 hafta var, kısa hafta yok (vadelide 1).
- Testler: DST geçişleri, Cumartesi artığı, Pazar açılışı ve 4S kış kayması birim testle doğrulandı. TR günlük barlar, bağımsız bir yöntemle (UTC+3 kaydırıp `resample('D')`) birebir aynı çıkıyor.

## 3. Gün kalitesi filtresi (sonuçlara bakılmadan sabitlendi)
`day_quality()`: Günün 1dk bar sayısı enstrüman medyanının %80'inin altındaysa gün geçersiz. CME FX'te ayrıca günlük hacim önceki 20 günün medyanının %25'inin altındaysa geçersiz. 2026'ya düşen artık da geçersiz. Olay hesabı D−1'e de baktığı için iki gün birlikte kontrol edilir.

| | TR günü (geçersiz / toplam) | NY17 günü | Geçersiz günler neler |
|---|---|---|---|
| EURUSD | 6 / 1567 | 4 / 1565 | 25 Ara, 1 Oca ve **2–5 Aralık 2024 Dukascopy boşluğu** (20 saatlik açıklar) |
| GBP, CAD, CHF | 3 / 1567 | 1 / 1565 | 25 Ara, 1 Oca |
| AUDUSD (6A) | 39 / 1555 | 36 / 1551 | ABD tatilleri (CME yarım gün) ve **roll öncesi Cumalar** |
| USDJPY (6J) | 40 / 1555 | 36 / 1551 | aynı |
| XAUUSD (GC) | 26 / 1553 | 22 / 1549 | tatiller, kısa seanslar |

- **Roll öncesi Cumalar:** Sürekli seri bu günlerde vadesi dolan ince kontratta kalıyor. Örnek 6A, 11 Eylül 2020: hacim 4.379 (normalde ~75 bin), 656 dk. Günlük H/L güvenilmez.
- **GC'de hacim filtresi kullanılmıyor:** `GC.n.0` açık pozisyona göre roll ediyor; roll öncesi hacim düşse de (ör. Mart 2020'de 47 bin) dakika sayısı tam ve fiyat likit. Hacim filtresi burada 86 sağlam günü atardı.

## 4. Vekil enstrümanlar: spot ile vadeli karşılaştırması
Kalibrasyon için önce iki parite kullanıldı (6E~EURUSD, 6B~GBPUSD). Spot veri gelince 6A~AUDUSD ve 6J~USDJPY de eklendi. Gün sınırı NY17.

| | 6E~EURUSD | 6B~GBPUSD | 6A~AUDUSD | 6J~USDJPY |
|---|---|---|---|---|
| Günlük getiri korelasyonu (roll dışı) | 0,998 | 0,998 | 0,998 | 0,998 |
| MA günlük durum sınıfı uyumu (flow/CRT/inside/kararsız) | %96,0 | %95,2 | %95,0 | %92,9 |
| **15dk marubozu sıklığı (açılış = uç, tam eşitlik)** | spot **%9,3** · vadeli **%17,3** | spot **%8,2** · vadeli **%22,7** | spot **%9,4** · vadeli **%20,9** | spot **%8,5** · vadeli **%20,7** |
| aynı, 0,5 pip toleransla | spot %32,3 · vadeli %35,7 | spot %26,0 · vadeli %22,7 | spot %32,1 · vadeli %37,6 | spot %27,2 · vadeli %20,7 |
| aynı, 1 pip toleransla | spot %49,4 · vadeli %50,2 | spot %40,1 · vadeli %44,6 | spot %50,1 · vadeli %54,1 | spot %41,3 · vadeli %32,6 |

Dört çiftte de aynı tablo var: günlük yapıda vadeli iyi vekil, marubozu sıklığında kötü vekil. Artık spot olduğu için vekil yalnız çapraz kontrol.

- **MA, ME, MD, MF (günlük/haftalık/4S/30dk yapı):** Vadeli iyi bir vekil. Durum sınıflarının %95–96'sı aynı çıkıyor. AUDUSD (6A) ve USDJPY (6J) bu modellerde kullanılabilir.
- **MB (marubozu):** Vadeli kötü bir vekil. Fiyat ızgarası kaba olduğu için (6A 0,5 pip, 6B 1 pip) "açılış = low" vadelide iki kat sık oluşuyor. Monarus'un iddiası FXCM 5 haneli kotasyonda; bizim 5 haneli spot verimizle uyumlu olan yalnız GBPUSD. Kullanıcı kararı gerekiyor (§7, Soru 2).
- **6J ters çevrim:** USDJPY = 1/6J. High ve low yer değiştiriyor (testle doğrulandı). Ölçek ~108–158 yen.

## 5. Maliyetler (data/CLAUDE.md §8), pip cinsinden
| Enstrüman | Gidiş-dönüş toplam |
|---|---|
| EURUSD / GBPUSD / USDCAD / USDCHF spot | 1,0 / 1,3 / 1,5 / 1,5 pip |
| AUDUSD (6A) | $5 + 2 × 1 tick = 1 tick + 2 tick = 3 tick = **1,5 pip** |
| USDJPY (6J) | $5 (≈0,8 tick) + 2 tick ≈ 2,8 tick; yen cinsinden fiyata bağlı: **~1,7 pip (110) – ~3,2 pip (150)**. Tick uzayında uygulanır |
| XAUUSD (GC) | $5 (0,5 tick) + 2 tick = 2,5 tick = **$0,25/oz** |
| NQ | $4 + 2 × 1 tick (Dreyko ile aynı) |

## 6. NQ (MC)
Dreyko Faz 0'ı aynen geçerli (`Dreyko/faz0/faz0_rapor.md`): bütünlük temiz, bar etiketi açılış, `session_date` DST hatası `load_is()` ile düzeltiliyor. `monarus_data.load("NQ")` bu yükleyiciyi çağırıyor. MC'nin 15dk barları 09:30 NY'ye hizalı. **Önceden tanımlı filtre:** CME erken kapanış ve RTH'siz günler (52 + 17) MC'de dışlanır (Dreyko'daki öneriyle aynı).

## 7. Kullanıcı kararı gereken konular

### Soru 1: Gün sınırı yeniden değerlendirilmeli (MA, ME, MF). **Karar: ana NY 17:00**
7 Kasım kararı: ana test TR 00:00, sağlamlık testi NY 17:00. Faz 0'da bu kararı değiştirebilecek bir bulgu çıktı:
- TradingView'de FX ve kripto günlük/4S mumları **borsanın seansına** göre çiziliyor. Grafik saat dilimi yalnızca etiketleri değiştiriyor (FXCM: NY 17:00; OKX: 00:00 UTC). Bu bir platform bilgisi; elimizdeki veriyle doğrulanamaz.
- Videolar bunu destekliyor:
  - **BTC:** Monarus BTC'de 4S kapanışlarını TR 07:00'den itibaren sayıyor (aoGM). Mumlar TR saatine hizalı olsaydı 4S kapanışı 04 ya da 08 olurdu. 03/07/11/15 dizisi ancak UTC'ye hizalı mumlarla çıkar.
  - **FX:** Bloklar TR 04/08/12/16 sayılıyor. Bu, yazın NY 17:00 hizasıyla birebir aynı. Örnekler Eylül–Ekim 2025'ten, yani yaz saati döneminden.
- **Sonuç:** Monarus'un "TR 00:00" günü yazın aslında NY 17:00 günü. Kışın onun mumları TR 01:00'de başlıyor.
- **Öneri:** Ana test NY 17:00 olsun (gün sınırı ve 4S blokları), TR 00:00 sağlamlık testi olsun. İki tanım yılın ~yarısında zaten aynı.
- **Dokunmayan kurallar:** Saat pencereleri (MB 08–18, MD 09–17, MA-T 09–19 TR) duvar saati kuralı. Bunlar TR saatinde kalır.

### Soru 2: MB hangi enstrümanlarda test edilsin? **Karar: GBPUSD ana + EURUSD/USDCAD/USDCHF spot; AUDUSD/USDJPY spot indirilecek, 6A/6J MB'de kullanılmaz**
- **Öneri:** Ana test GBPUSD spot, tam eşitlikle (O = L). Bu, iddianın kotasyon hassasiyetine en yakın test.
- AUDUSD (6A) ve USDJPY (6J) "vekil" etiketiyle ikincil test olsun; marubozu tanımı bunlarda tick fiyatında tam eşitlik.
- **Sonuç dili:** Vekilde marubozu iki kat sık oluşuyor. Bu yüzden vekil sonuçları iddiayı ne çürütür ne de destekler; raporda yalnız ek bilgi olarak geçer.
- **Alternatif:** Spot EURUSD, USDCAD ve USDCHF'i de eklemek. Monarus EUR için "verimli değil" diyor; eklenirse bunu genelleme testi olarak sunarız, iddianın testi olarak değil.

## 8. Dosyalar
- `monarus_data.py`
  - `load(name)`: IS yükleyici. Spot; 6A/6J/6E/6B ratio-ayarlı (`adjusted=False` ile tick fiyatı); GC fark-ayarlı; NQ Dreyko yükleyicisinden.
  - `daily`, `weekly`, `hours4`, `intraday`: gün sınırı `tr` ya da `ny17`. Barlarda `n_min`, `t_open`, `t_last`, `has_roll` kolonları var.
  - `day_quality(d, name)`: gün kalitesi filtresi (§3).
- Dosyadaki `ATR_14_d1`, `PDH` gibi hazır kolonlar kullanılmıyor (vadelide ayarsızlar). Her öznitelik ayarlı seriden yeniden hesaplanacak.
- **Veri dosyalarına yazılmadı.**

## 9. Ek veri: AUDUSD ve USDJPY spot (8 Kasım, kullanıcı isteği)
- **Pepperstone:** Hesapsız, doğrudan indirilebilir ücretsiz 1dk geçmiş veri bulunamadı. Fiyat geçmişine yalnızca MT4/MT5 içinden (History Center, Strategy Tester) erişiliyor. Ayrıca mevcut 4 parite Dukascopy bid olduğu için, farklı bir broker tutarlılığı bozardı.
- **Yöntem:** Dukascopy datafeed `BID_candles_min_1.bi5`, günlük dosyalar, 2020-01-01 – 2026-11-06. 2026 kullanıcı isteğiyle ayrı adımda indirildi; yalnız yapısal kontrol yapıldı (satır sayısı, tarih aralığı). Script'ler `veri_ek/scripts/` altında.
- **Doğrulama:**
  - Ham dönüşüm: Aynı yöntemle EURUSD 2023'ten 66 gün (82.260 dk) çekildi; mevcut ham dosyayla dakika dakika birebir aynı (%100).
  - İşlenmiş dosya: `islenmis.py`, mevcut dosyaları üreten pipeline'ın kopyası. Aynı script mevcut EURUSD işlenmiş dosyasını (2.547.215 satır, 32 kolon; günlük 1.772 satır) birebir yeniden üretti. Yeni dosyaların şeması mevcut spotlarla aynı.
  - Yükleyici: `load("AUDUSD")` işlenmiş dosyadan okuyor. Ham yıllık dosyalardan bağımsız yükleme (`load_spot_ext`) ile birebir eşit (test). Tek fark, 31 Ara 2025 NY 17:00 sonrası 120 dakika; bu dakikalar 2026 işlem gününe ait ve OOS olarak atılıyor.
- **Hafta sonu kuralı:** Ham veriden işlenmiş veriye geçişteki kural: Cumartesi, Pazar NY 17:00 öncesi ve Cuma NY 17:00 sonrası barlar atılıyor. Kural EURUSD, GBPUSD ve USDCHF'te 2020–2025 boyunca birebir tuttu (0 fark).
- **Sonuçlar (IS 2020–2025):**

| | AUDUSD | USDJPY |
|---|---|---|
| Satır | 2.254.920 | 2.254.920 |
| Eksik gün / mükerrer / NaN / High<Low / O-C aralık dışı | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 |
| Gün sayısı (NY17), geçersiz gün | 1.566, 0 | 1.566, 0 |
| 15dk / 30dk doluluk (TR 08–18) | %100 / %100 | %100 / %100 |
| Haber barı range'i m−1 / **m+0** / m+1 (NFP, pip) | 2,8 / **23,0** / 8,6 | 5,2 / **43,1** / 13,8 |

  TR sınırında 2026-01-01 (TR) günü geçersiz sayılıyor. Bu, 31 Aralık 21:00–22:00 UTC arasındaki 60 dakikalık kalıntı; diğer spotlarda da aynı.
- **Bilinen fark:** Mevcut 4 paritenin dosyalarında bazı tatil/kesinti günlerinin düz barları eksik (ör. EURUSD 2020-12-25, 2024-12-02..05). Yeni iki paritede bu dakikalar Dukascopy'nin verdiği gibi düz bar (O=H=L=C) olarak duruyor. Gerçek işlem barlarında fark yok. Gün kalitesi filtresi buna göre değişmiyor (dakika sayısına bakıyor, düz barlar da sayılıyor). Not: Bu günler düz bar yüzünden "tam" görünür; olay tespitinde düz barlar fiyat hareketi üretmez.
- **Maliyet:** Spot AUDUSD/USDJPY için `data/CLAUDE.md` §8'de varsayılan yok. Backtest'ten önce belirlenmeli (öneri: spread yapısı benzer olduğundan EURUSD/GBPUSD aralığı, 1,0–1,5 pip; karar kullanıcıda).
- **data/ yerleşimi:** `data/FX_Currencies/dukascopy_spot/raw/{audusd,usdjpy}_{2020..2026}.parquet`, `raw/dukascopy_bi5/{AUDUSD,USDJPY}/…` (4.843 günlük dosya), `processed/fx_dukas_{audusd,usdjpy}_{1m_processed,daily_summary}.parquet`. `dukascopy_data_summary.json` güncellendi (önceki sürüm `processed/_backup_pre_audusd_usdjpy/`). `data/CLAUDE.md` §5 envanteri güncellendi.
