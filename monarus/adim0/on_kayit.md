# Adım 0 ön kaydı (Monarus, MA–MF) — sonuçlardan ÖNCE yazıldı, 2026-11-08

Kullanıcı onayı: 8 Kasım ("Evet, Adım 0'a geç"). Bu bir **olay çalışmasıdır, backtest değildir**: portföy, pozisyon boyutu, eşzamanlı işlem kısıtı ve parametre taraması yok. Etiketler tek tek olayın ileriye dönük sonucudur. Bu belgedeki tanım, eşik ve ölçütler sonuç görüldükten sonra değiştirilmez. Değişirse karar günlüğüne "sapma" diye yazılır.

## 0. Ortak kurallar
- **Veri:** Yalnız IS, 2020-01-01 – 2025-12-31 UTC (`faz0/monarus_data.py`). 2026'ya dokunulmaz.
- **Enstrümanlar:**
  - FX6: EURUSD, GBPUSD, USDCAD, USDCHF, AUDUSD, USDJPY (spot, Dukascopy).
  - XAUUSD: GC vadeli, fark-ayarlı.
  - NQ: yalnız MC.
  - MB yalnız FX: ana olarak iddianın 3 paritesi (GBPUSD, AUDUSD, USDJPY), genelleme için EURUSD, USDCAD, USDCHF.
- **Gün sınırı:** Ana NY 17:00 (`ny17`); günlük ve 4S bloklar buna hizalı. Sağlamlık TR 00:00 (`tr`) yalnız MA, ME, MF ve MD'de. Saat pencereleri TR duvar saatidir (sabit UTC+3).
- **Gün kalitesi:** Faz 0 ön kaydı. Kullanılan her günlük bar (D−1, D, D+1, …) geçerli olmalı. Haftalık barda, haftanın tüm günleri geçerli olmalı.
- **Zaman semantiği:** Bar etiketi açılış zamanıdır. Üst zaman dilimi (HTF) barı, son 1dk barı kapandığında bilinir. Market giriş, sinyal barının kapanışından sonraki ilk 1dk barın açılışındadır.
  - Limit/stop girişleri 1dk barda dolar. Dolum barında hedef sayılmaz, stop sayılır (SL-first, muhafazakâr).
  - Boşlukla açılış stopun ötesindeyse çıkış açılış fiyatından (daha kötü olan).
- **Pivot (swing):** Fraktal uzunluk L: bar, iki yanındaki L barın hepsinden yüksek (düşük) ise pivottur. Pivot, L bar sonra (sağ taraf kapandığında) bilinir. L değerleri: MB 5 (göstergedeki "(5)"); MD, MF, MA-T ve MC 2.
- **ATR:** Günlük TR'nin 14 günlük ortalaması, yalnız tamamlanmış önceki günlerden (shift 1), aynı gün sınırıyla. Getiriler ATR ile normalize edilir.
- **İşlem tipi olay etiketleri** (MA-T, ME, MF, MB, MD, MC):
  - `R`: SL-first sonuç (R cinsinden). Önce TP → +R_tp; önce stop → −1 (boşlukta daha kötü). Süre sonunda açıksa son fiyattan piyasa değeri.
  - `hit`: süre sınırından önce TP'ye stoptan önce ulaşma.
  - `R_net`: R − maliyet/stop mesafesi. Maliyetler gidiş-dönüş:
    - EURUSD 1,0 pip; GBPUSD 1,3; USDCAD 1,5; USDCHF 1,5.
    - AUDUSD ve USDJPY spot için **geçici** 1,3 pip (data/CLAUDE.md'de değer yok; kullanıcı backtest öncesi belirler).
    - XAUUSD $0,25; NQ 0,7 puan.
  - `mirror`: aynı giriş anı ve fiyatında **ters yönlü ayna işlem**: stop aynı mesafede karşı tarafta, TP aynı R katında. Tarafsız iki yönlü kıyas (H0) budur.
  - MFE/MAE (R), +1S / +4S getirisi (yönlü, ATR cinsinden), gün sonu (NY17) getirisi.
  - Koşulsuz baz: aynı enstrümanda aynı TR saat:dakikasında tüm günlerin ortalama getirisi. Fazla getiri bu bazdan farkla ölçülür.
- **Süre sınırı:** MB, MD ve MF'de 5 işlem günü; MA-T ve ME-1'de D+1 gün sonu; ME-2'de bias haftasının sonu; MC'de aynı gün 16:00 NY.
- **Olay sıklığı:** Model + varyant + enstrüman + gün başına en fazla 1 olay (günün ilki). Monarus'un "2 deneme" (MF) ve gün içi çoklu işlem ayrıntıları ilk turda yok.
- **İstatistik:**
  - Her anahtar (model × varyant × enstrüman × gün sınırı) ve alt küme (tümü, long, short) için: n, hit, ortalama/medyan R ve R_net, t ve p değeri, ayna farkı (eşli t), yıl istikrarı (aynı işaretli yıl/6).
  - Tüm p-değerleri tek havuzda Benjamini–Hochberg ve Bonferroni ile düzeltilir. Test sayısı `out/meta.json`'a yazılır ve deneme sayacına işlenir.
  - Ağaç modeli + permutation importance (Leave-One-Year-Out), n ≥ 300 olan ana anahtarlarda. Öznitelikler: stop/ATR, TR saati, haftanın günü, yön, ATR rejimi (60 günlük yüzdelik, nedensel), D−1 range/ATR.
- **Okuma ölçütü (Adım 0, backtest kararı için öneri; karar kullanıcıda):**
  - Bir anahtar **"aday"** sayılması için ana alt kümede şu üçü birden gerekir:
    - (a) ortalama R_net > 0 ve BH q < 0,05;
    - (b) ayna farkı > 0 ve BH q < 0,05;
    - (c) en az 4/6 yılda aynı işaret.
  - Biri eksikse "zayıf", hiçbiri yoksa "ret". İddia rakamıyla (WR) kıyas ayrıca raporlanır.
- **Sızıntı testi:** Pertürbasyon. Karar anından sonraki 1dk barlar bozulur, olay listesi (zaman, yön, giriş, stop, TP) değişmemeli. Her model için birim test.
- **Doğrulama:** Videodaki IS örnek günleri (2025 Eylül–Ekim vb.) yakalanıyor mu, kontrol edilir. Yakalanmayan örnek varsa nedeni rapora yazılır.

## 1. MA: günlük bias isabeti (iddia I-MA2) + MA-T işlem katmanı
- **Durum:** Model taslağındaki tablo. D'nin durumu, D+1 için bias.
  - Flow long: C > H₋₁.
  - Flow short: C < L₋₁.
  - CRT short: H > H₋₁, C ≤ H₋₁, L ≥ L₋₁.
  - CRT long: L < L₋₁, C ≥ L₋₁, H ≤ H₋₁.
  - Inside ve kararsız: bias yok.
- **Hedef:** Long bias'ta H_D, short bias'ta L_D.
- **Etiketler (D+1):**
  - `hit_bias`: hedefe değme (long: H_{D+1} ≥ H_D).
  - `hit_opp`: karşı uca değme (long: L_{D+1} ≤ L_D).
  - `first_bias`: 1dk barlarla hangisine önce değdiği. Aynı dakikada ikisi birden → karşı uç önce sayılır.
  - `ret_cc`: (C_{D+1} − C_D)/ATR, bias yönünde.
- **Testler:**
  - MA-1: P(hit_bias) − P(hit_opp), aynı günler, eşli.
  - MA-1b: P(first_bias) − 0,5.
  - MA-0 baz: P(hit_bias), tüm günlerde aynı yönlü hedefe değme oranıyla iki oranlı z testiyle kıyaslanır.
  - MA-r: ortalama yönlü `ret_cc`, tüm günlerin ortalama `ret_cc`'sine göre fark.
  - Alt kümeler: flow / CRT, long / short.
- **İddia kıyası:** Monarus'un tablosu (EUR %71,9, GBP %66,9, AUD %66,8, CAD %80,1, CHF %68,3, XAU %60,7) `hit_bias` ile yan yana konur.
- **MA-T:**
  - D+1'de 09:00 TR sonrası fiyat, D range'inin %50 seviyesinin ucuz tarafına geçmiş olmalı (long bias: altına). Hedef bundan önce alınmışsa gün iptal.
  - 1S konfirme: 09:00 TR'den beri en düşük low'u yapan 1S mumun high'ının üstünde 1S gövde kapanışı. Short simetrik.
  - Market giriş. Stop = 09:00'dan girişe kadarki en düşük low. TP = günlük hedef.
  - RR < 1,8 ise ana varyantta işlem yok (limit varyantı ilk turda yok). Konfirme kapanışı ≤ 19:00 TR.

## 2. ME: CRT
- **ME-1:** D+1 MA bias'lı gün.
  - 4S bloklar ny17 hizasında (00/04/08/12/16/20; yazın TR saatiyle aynı).
  - Çiftler: (04→08, giriş 12:00) ve "S+" (08→12, giriş 16:00).
  - 2. mum, 1. mumun bias'a karşı ucunu fitille alır ve 1. mumun içinde kapanır (long: L₂ < L₁, C₂ ≥ L₁; ayrıca C₂ ≤ H₁).
  - Giriş 2. mum kapanışında market. Stop 2. mumun ucu. TP günlük MA hedefi; giriş anında hedef zaten geçilmişse olay yok.
  - Günde ilk tetik.
- **ME-1n:** Bias filtresiz aynı 4S CRT; iki yön de, her gün. Negatif kontrol.
- **ME-2:**
  - Haftalık durum (MA tablosunun haftalık hali) → hafta W+1 bias'ı.
  - W+1 içinde günlük CRT: k günü, k−1'in bias'a karşı ucunu alıp içeride kapanır.
  - k+1 açılışında market. Stop k'nın ucu. TP haftalık hedef (long: H_W).
  - Süre sınırı W+1 sonu. Haftada ilk tetik.

## 3. MF: haftalık bias + PDH/PDL sweep + 15dk CHoCH (97GD, iddia I-MD3)
- **Haftalık bias:** C_W > H_{W−1} → W+1 long; C_W < L_{W−1} → short. Tolerans 0 (ana).
  - MF-1: kararsız (içeride kapanan) hafta → işlem yok.
  - MF-1k: kararsız haftada son kırılım yönü devam eder.
  - MF-n: bias'sız, iki yön; negatif kontrol.
- **Tetik (D günü, long):** Fiyat PDL'nin (D−1 low) altına iner.
  - Sweep derinliği > 30 pip (XAU'da 0,4 × ATR) olursa gün iptal.
  - Sağlamlık: hepsinde 0,4 × ATR.
- **CHoCH (15dk, long):** Sweep dibini yapan 15dk mumdan geriye, highları azalan ardışık mumlar (düşüş bacağı) izlenir. Bacağın ilk mumu ile sweep mumu arasındaki en yüksek high = CHoCH seviyesi.
  - Fiyat bu seviyeyi aşınca (fitil dahil, 1dk) giriş seviyeden dolar (boşlukta açılıştan).
  - Short simetrik.
- **Stop:** Girişe kadarki sweep ucu.
- **TP:** Girişten önce bilinen en yakın 15dk pivot (L=2) likiditesi. Long için girişin üstündeki en yakın pivot high. Pivot yoksa olay yok. Min RR yok.

## 4. MB: marubozu 1:1 (iddia I-MB1/2)
- **15dk barlar.** Trend: kapanış MA'nın üstünde ve internal yapı bullish (son kırılım: kapanışın son onaylı pivot high'ı geçmesi; L=5). Short simetrik.
  - **MB-v:** MA = SMA(21). Spot veride hacim yok; VWMA(21)'in yerine SMA(21). Sapma olarak kayıtlı.
  - **MB-s:** MA = WMA(26) üzerine SMA(5). "SWMA(26,5)" için yorum, belirsiz.
- **Marubozu:** Long bullish mum, O = L (tam eşitlik). İtki bacağında olmalı: high, son onaylı pivot low'dan beri en yüksek high.
- **Sinyal:** Kapanış TR 08:00–18:00 içinde.
- **Giriş:** Marubozu açılışına limit. Kapanıştan sonraki 10 mum (150 dk) içinde dolmalı ve dolum TR 08–18 içinde olmalı.
- **Stop:** Son onaylı pivot low − 1,5 pip. Mesafe > 20 pip ise olay yok.
- **TP:** 1R. Süre sınırı 5 gün.
- **H0-MB:** Trend ve yapı filtresi olmadan, penceredeki tüm marubozular (aynı giriş, stop, TP). Ayrıca ayna.
- İlk turda yok: FVG stop filtresi (MB-1F) ve kâr sonrası geri çekilme varyantı.

## 5. MD: HTF FVG + 30dk sweep + MSB (I-MD1/2/4)
- **POI:** 3 mumluk FVG (bullish: L_i > H_{i−2}), i barının kapanışında bilinir.
  - Aktif koşulu: bölgenin dibi (bullish) aşağı geçilmemiş ve yaş ≤ 5 işlem günü.
  - Bias = en güncel aktif FVG'nin yönü. Daha yeni ters FVG bias'ı çevirir.
  - Varyant HTF: **MD-4S** (4S FVG) ve **MD-1G** (1G FVG).
- **Tetik (long):**
  - 30dk low bölgeye girer (≤ üst sınır).
  - Bölge içinde oluşmuş bir 30dk pivot low (L=2) bir sonraki 30dk mumla fitille alınır.
  - Sonra sweep'ten önceki en son onaylı 30dk pivot high'ın üstünde 30dk kapanış olur (MSB).
  - MSB kapanışı 09:00–17:00 TR içinde (17:00 kapanışı dahil).
- **Stop:** Sweep'ten MSB'ye kadarki en düşük low.
- **TP:** Girişten önce bilinen, girişin üstündeki en yakın 30dk pivot high. RR < 1,8 → olay yok.
- **Giriş varyantları:**
  - **MD-a:** MSB kapanışında market.
  - **MD-b:** MSB bacağında (sweep dibinden MSB'ye) oluşan en son bullish 30dk FVG'nin üst sınırına limit. 10 × 30dk içinde dolmalı. RR dolum fiyatıyla yeniden hesaplanır.
- **Ablasyon:**
  - MD-n0: POI'siz (30dk sweep + MSB, iki yön).
  - MD-n1: 1,8R filtresiz (TP aynı en yakın likidite).
- Toplam varyant: {4S, 1G} × {a, b} + n0 × {a, b} + n1-a.

## 6. MC: NQ 15dk (I-MC1, iddianın kendisi OOS)
- **15dk barlar, 09:30–13:00 NY.** Günde ilk tetik. Cuma 12:00 NY sonrası giriş yok.
- **MC-A (long):**
  - Sweep: 09:30'dan beri en az 2 tamamlanmış 15dk mumun en düşük low'unun altına inen mum.
  - Onay seviyesi: sweep mumu ve ondan önceki ardışık ayı (C < O) mumlarının en erkenindekinin açılışı (CISD).
  - Bu seviyenin üstünde 15dk gövde kapanışı → market giriş.
  - İptal: onaydan önce karşı tarafın (09:30'dan beri en yüksek high) alınması.
- **MC-B (long):** Sweep mumu bullish ve bir önceki mumun gövdesini engulf eder (C > önceki O ve C > önceki C, O ≤ önceki C). Önceki mumun gövde üst sınırına (max(O, C)) limit, 13:00'e kadar.
- **Stop:** Sweep ucu. **TP:** 1,5R.
- **Stop filtresi:** Mesafe fiyatın %0,5'inden büyükse olay yok; ikinci varyantta %1.
- **BE varyantı:** +1R'de stop girişe.
- **H0:** Aynı gün, 09:30–13:00 arasında rastgele dakika ve yön, aynı stop mesafesi ve 1,5R (500 tekrar). Ayrıca ayna.
- Belirsiz: "likidite"nin tanımı, market/limit tutarsızlığı. Konsolidasyon filtresi kodlanmaz.

## 7. Kapsam dışı (ilk tur)
- MB-1F, MB kâr sonrası geri çekilme, MF 2. deneme ve %50 + BE çıkışı, MA-T limit girişi, ME Key Level, MD PDH/PDL/DXY kesişimi ve haber filtresi.
- Bunlar ancak ana test sonucundan bağımsız gerekçeyle ve yeni ön kayıtla eklenebilir (post-hoc etiketli).
