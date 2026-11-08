# Monarus: kodlanabilir model taslağı (7 Kasım 2026; MD ve MF adayı 8 Kasım, Gemini pencere 2 sonrası)

**Kaynaklar:** `screening_ozet.md` (33 içerik, 1–5 skala), `screening_A/B/C.md`, `gemini/notes.md` (Argon: Sk5, Uzd, aoGM, 8YMu, pchmm, 97GD), iddialar `karar_gunlugu.md` → "İddia kaydı".

**Durum:** Bu belge hipotez adayıdır, bulgu değildir. Adım 0 (olay çalışması) sonuçları raporlanmadan ve kullanıcı onay vermeden backtest yok (CLAUDE.md §3). 2026 kilitli OOS; Monarus'un 2026 backtest'leri (MC tamamen, MB kısmen) yalnızca iddia olarak kayıtlı.

**Dreyko'dan farkı:** Monarus'ta tek bir model yok. Ortak omurga **"üst zaman dilimi mum ilişkisiyle bias + alt zaman diliminde onaylı giriş"**. Beş aday ayrı ayrı test edilir (bağımsızlık, §1.5 tekil kârlılık).

---

## MA: Günlük bias motoru (Uzd, aoGM, EAL, 97G)

**İddia (I-MA2):** Bias yönünde ertesi gün hedefe değme oranı 21 yılda %60–80 (pariteye göre). Monarus bunu bir işlem WR'si değil, bias isabeti olarak sunuyor. Bu yüzden **önce tam bu iddia test edilir**, sonra işlem katmanı.

**Kurallar (günlük mum, PDH/PDL fitilden; kırılım gövde kapanışıyla):**

| Durum (D günü, D−1'e göre) | Koşul | D+1 bias | D+1 hedefi |
|---|---|---|---|
| Flow long | C_D > H_{D−1} | long | H_D (bias mumunun kendi high'ı) |
| Flow short | C_D < L_{D−1} | short | L_D |
| CRT short | H_D > H_{D−1} ve C_D ≤ H_{D−1} (low alınmamış) | short | L_D (CRT mumunun kendi low'u) |
| CRT long | L_D < L_{D−1} ve C_D ≥ L_{D−1} (high alınmamış) | long | H_D |
| Inside | H_D ≤ H_{D−1} ve L_D ≥ L_{D−1} | yok (konsolide) | — |
| Kararsız | H_D > H_{D−1}, L_D < L_{D−1}, L_{D−1} ≤ C_D ≤ H_{D−1} | yok | — |
| Outside + dışarıda kapanış | iki uç alınmış, C_D dışarıda | flow ile aynı | flow ile aynı |

- **Açık uçlar:** Inside/kararsız gün sonrası "ana mumun dışında kapanış bekle" kuralı (bias'ın birkaç gün taşınması). aoGM'deki "bullish CRT'nin ertesi günü bearish CRT → plan iptal" zaten tablodan çıkıyor. CRT mumunun rengi tanımsız.
- **Gün sınırı:** Monarus'un grafikleri **UTC+3 00:00** (TR gece yarısı; FXCM/OANDA). Standart FX günü NY 17:00. → Soru 2.
- **İşlem katmanı (MA-T, Uzd 1S girişi):** D+1'de 09:00 TR sonrası, önceki günün Fib 0.5'i ucuz/pahalı tarafına geçilmiş olmalı (hedef 0.5'ten önce alınırsa gün iptal). 1S konfirme: son swing yapan 1S mumun karşı ucunun ötesinde gövde kapanışı. Market giriş (RR < 1.8 ise konfirme seviyesine limit). Stop son 1S swing ucu, TP günlük hedef, min RR 1.8, giriş ≤ 19:00 TR.

**Hipotezler:**
| Kod | Ölçülen | Kıyas |
|---|---|---|
| MA-0 | Koşulsuz: D+1'in H_D'yi aşma oranı / L_D'nin altına inme oranı (her gün) | **Baz.** Hedef bias mumunun kendi ucu olduğu için baz oran yüksek olabilir |
| MA-1 | Monarus bias'ı: P(D+1 hedefe değer \| bias) | MA-0 ve **ters yönlü** hedefe değme oranı (aynı günlerde) |
| MA-2 | Alt kümeler: flow vs CRT, long vs short, yıl | — |
| MA-T | İşlem katmanı, olay çalışması: 1S konfirme sonrası +N saat ve gün sonu getiri (ATR'ye göre) | Aynı günlerde koşulsuz 1S konfirme |
| H0 | Rastgele yön, aynı günler | — |

---

## MB: Marubozu 1:1 (Sk5 + 6 short)

**İddia (I-MB1/2):** 3 paritede 5–6 aylık backtestlerde WR ≥ %75; 17 işlemde %88.24.

**Kurallar:**
- **Enstrüman/TF:** GBPUSD, AUDUSD, USDJPY; 15dk. Saat 08:00–18:00 TR (UTC+3), giriş yalnızca bu aralıkta.
- **Trend:** Fiyat **VWMA(21)** üstünde ve internal yapı yukarı (son internal kırılım bullish BOS/CHoCH) → yalnız long. Short simetrik.
- **Marubozu (long):** alt fitil yok (O = L), bullish mum; yeni internal high yapan **itki bacağında**. Short: O = H.
- **Giriş:** marubozunun **açılışına limit**; marubozu kapandıktan sonra **10 mum** içinde dolmazsa iptal.
- **Stop:** son internal swing low'un **1–2 pip** altı; **maks 20 pip** (üstü işlem yok). Hemen altında dolmamış FVG varsa stop FVG altına ya da işlem yok (ikincil filtre).
- **TP:** 1R. Zaman çıkışı tanımsız (açık işlem taşınabilir).
- **Gün içi kâr sonrası** geri çekilme bacağındaki marubozular da serbest (ikincil varyant).
- **Göstergeler:** "Market Structure (Choch/BOS) (5)", büyük olasılıkla pivot uzunluğu 5 (?). Grafikte "SWMA(26,5)" görünüyor ama kural metni VWMA 21 diyor. → Soru 3.

**Hipotezler:** MB-1 (çekirdek: VWMA + internal + marubozu limit + 10 mum + 20 pip + 1R), MB-1F (+FVG stop filtresi), H0 (aynı saatte rastgele marubozu, trend filtresiz; ve ters yön). Adım 0'da **olay = marubozu limitinin dolması**; ölçülen: dolumdan sonra +1R'ye stopdan önce ulaşma oranı (SL-first), koşulsuz tüm marubozu dolumlarına ve trend tersi dolumlara göre. 1:1'de başabaş WR ≈ %50 + maliyet; 10–15 pip stopta 1 pip spread bile başabaşı ~%54'e çeker.

---

## MC: NQ 15dk açılış-sonrası sweep (Y4 canlı yayın)

**İddia (I-MC1):** 2026 Mar–Ağu ay ay sayım (~%74 WR, ~+38R), BE işlemleri sayım dışı. 2026 = OOS; test IS 2020–2025'te sıfırdan.

**Kurallar:**
- NQ 15dk, 09:30–13:00 NY (Monarus: 16:30–20:00 TR yaz saati; DST farkını kendisi söylüyor → NY saatiyle tanımlanır). Açılış öncesi bias yok, iki yönlü. Günde tek işlem; Cuma geç saat yok.
- **Tetik A (sweep + CISD):** açılış sonrası fiyat **en az 2 mumun** ucunu süpürür; ardından son karşı swing'in (onay seviyesi) ötesinde **gövde kapanışı** → giriş. Onay gelmeden ters taraf süpürülürse ya da ters gövde kapanışı olursa iptal.
- **Tetik B (sweep + engulf):** süpüren mum önceki mumu engulf eder → engulf edilen mumun gövdesine limit.
- **Stop:** sweep ucu. **TP:** sabit 1.5R. **BE:** +1R sonrası stop girişe (iki varyant: BE'li / BE'siz).
- **Filtre:** stop mesafesi fiyatın %0.5'i (veya %1'i) üstündeyse işlem yok. → Soru 4.
- **Belirsiz:** "likidite" = hangi mumların ucu (açılış sonrası 15dk mumlar mı, açılış öncesi dahil mi); market/limit (A'da tutarsız); konsolidasyon filtresi (tanımsız, kodlanmaz).

**Hipotezler:** MC-A, MC-B, MC-A∪B (günün ilk tetiği); H0 = 09:30–13:00'te rastgele yön, aynı stop/TP geometrisi. Not: NQ 09:30 sweep fikri Dreyko'da test edildi; bağımsızlık ilkesi gereği o bulgu öncül alınmaz, MC kendi tanımıyla sıfırdan test edilir (yalnızca `load_is()` veri düzeltmesi taşınır).

---

## ME: Günlük bias → 4S CRT (aoGM Model 1) ve haftalık → günlük CRT (Model 2)

- **ME-1:** MA bias'ı olan günde, 4S mumlarda (TR saatiyle 04/08/12/16) 2. mum 1. mumun ucunu fitille alıp içeride kapanır; yön bias ile aynı → 2. mum kapanışında market. Sıralar: 04→08 (giriş 12:00) ve "S+" 08→12 (giriş 16:00). Stop 2. mumun ucu, TP günlük hedef (MA hedefi). Forex penceresi 08–16 TR. Key Level opsiyonel (ilk turda yok).
- **ME-2:** Haftalık bias (MA kurallarının haftalık hali) → günlük CRT → ertesi gün açılışında market; stop CRT ucu, TP haftalık hedef.
- **Hipotezler:** ME-1 (bias'lı), ME-1n (bias filtresiz 4S CRT = negatif kontrol, ablation), ME-2, H0.

---

## MD: Ana model, HTF FVG + 30dk sweep (8YMu, pchmm, U8, 3PGk, haftalık işlem videoları)

**İddia (I-MD1/2/4):** "parite başı 2–3 yıllık backtest" (sayı yok), "win rate'im %75", "ayda 6–10R / 8R". Kurallar kısmen kapalı ("5–6 sabit kural", "%20 inisiyatif").

**Kurallar (Gemini ekran okuması + transkript; iki video tutarlı olanlar):**
- **Enstrüman/TF:** FX (FXCM: GBPUSD, USDCHF, EURUSD…), altın/gümüş, US100/SPX, BTC. HTF **1G veya 4S**, giriş **30dk**. Saat UTC+3.
- **Bölge (POI):** Fiyatın son hareketinin bıraktığı **en güncel, doldurulmamış 1G veya 4S FVG** (3 mum boşluğu). Eski (5–10 gün) FVG yok. Yeni ters yönlü FVG oluşursa bias döner. 4S'te ters yönlü yeni FVG olmamalı (1G FVG kullanılıyorsa). PDH/PDL ve DXY teması opsiyonel kesişim (ilk turda yok).
- **Tetik:** Fiyat POI'ye pullback'le girer → 30dk'da **POI içinde yakın bir iç tepe (short) / dip (long) fitille alınır** (sweep).
- **Konfirme ("zayıflık"):** Sözlü tanım yok. Çizimler: sweep sonrası yükselişi başlatan son ara dibin aşağı kırılması (MSB/CHoCH). İki giriş varyantı:
  - **MD-a (pchmm):** kırılım mumunun **30dk kapanışında market** [pchmm 01:46].
  - **MD-b (8YMu):** kırılımın bıraktığı **30dk FVG'ye retest limiti** [8YMu 02:15, 06:40].
- **Stop:** sweep yapan 30dk fitilin ucu (ekran; sözlü kural yok).
- **TP:** 30dk'daki **en yakın karşı swing likiditesi**; karşıda ters 4S FVG varsa onun içindeki ilk likidite. **Min 1.8R**: en yakın likidite 1.8R vermiyorsa işlem yok [8YMu 07:20–07:46]. Kısmi kâr / BE yok.
- **Saat:** **FX'te konfirme 09:00–17:00 TR** (17:00 kapanışı dahil), sonrası ertesi gün [pchmm 01:16–01:32]. Endeks/emtiada kural yok. Haber öncesi çıkış (taramadan, U8) kodlanabilir değil → ilk turda yok.
- **Parametreler (plato ekseni, sonuçtan önce sabitlenecek):** pivot uzunluğu (iç tepe/dip ve "en yakın likidite" tanımı), FVG tazelik penceresi, retest bekleme süresi (MD-b).

**Hipotezler:** MD-a, MD-b; ablation: POI'siz 30dk sweep+kırılım (MD-n0), 1.8R filtresiz (MD-n1), 17:00 kuralsız; H0 = aynı saatlerde rastgele yön, aynı stop/TP geometrisi. Adım 0'da olay = konfirme anı; ölçülen: SL-first ile 1.8R+ hedefe stoptan önce ulaşma, +N bar getiri (ATR'ye göre), iki yön ayrı.

**Kodlanamayan:** "%20 inisiyatif" (haber, piyasa koşulu, psikoloji), "5–6 sabit kural"ın açıklanmayan kısmı, ekran başında stop taşıma. Kapsam dışı; iddiayı kurtaran bir kaçış yolu değil.

---

## MF (8 Kasım'da kullanıcı onayıyla kapsama alındı): Haftalık bias + PDH/PDL sweep + 15dk CHoCH (97GD, "fon sistemi")

**İddia (I-MD3):** WR "%68–80", kararsız hafta filtresiyle "80–85"; dayanak "tuttuğum veriler".

Bu, kanalın **en sayısal** ana-model anlatımı; MD'den (FVG + 30dk) ayrı bir model. Başlangıçtaki MA–ME seçiminde yoktu (tarama 97GD'yi MD'ye bağlamıştı); 8 Kasım'da kullanıcı kararıyla eklendi.

- **Haftalık bias:** Haftalık gövde, önceki haftanın H'si üstünde kapanırsa sonraki hafta yalnız long, L'si altında kapanırsa yalnız short. 1–3 pip içeride kalan kapanış da kırılım (tolerans parametresi). Kararsız hafta (gövde içeride): ana varyant **işlem yok** (iddia edilen "ince trik"); ikincil: önceki yönde devam.
- **Günlük tetik:** Long'da PDL, short'ta PDH alınır (fitil yeterli). Her gün yeni tetik.
- **İptal:** Sweep, PDH/PDL'nin **30–35 pip** ötesine geçerse o gün işlem yok. Sağlamlık: ATR'ye göre eşdeğer eşik. Kurulum başına en fazla **2 deneme**.
- **Giriş (15dk):** CHoCH seviyesi = sweep tepesindeki mumlardan önceki mumun ucunu geçemeyenin ters ucu (sağında daha uç fitil varsa o fitil). Bu seviyenin aşılması (fitil dahil) → market. CHoCH çok uzaksa internal BOS (ikincil, ilk turda yok).
- **Stop:** sweep ucunun fitili. **TP:** en yakın 15dk swing likiditesi (ana); %50 kâr + BE + PDL/PDH (ikincil). Min RR yok.
- **Saat:** Kural yok (FX 7/24 gün içi; gün sınırı MA ile aynı: TR 00:00).
- **Hipotezler:** MF-1 (kararsız hafta pas), MF-1k (kararsız haftada devam), MF-n (haftalık bias'sız PDH/PDL sweep + CHoCH = negatif kontrol), H0.

---

## Kodlanamayan / sübjektif kısımlar (kapsam dışı, kaçış yolu değil)
- MD'nin kapalı "5–6 kuralı", "%20 inisiyatif" filtresi ve "zayıflık"ın sözlü tanımı (çizimlerden MSB/CHoCH olarak kodlanıyor); Key Level (FVG/OB/arz-talep) seçimi; "konsolide bölge" sezgisi; "zorlama poz".
- MB'deki "son dip" seçimindeki takdir (pivot kuralıyla temsil edilir); MA'daki paylaşılmayan "Daily Bias" indikatörünün iç ayrıntıları (tablodaki sayımları birebir üretemeyebiliriz; sapma raporlanır).

## Kullanıcı kararları (7 Kasım 2026, sonuçlar görülmeden)
| # | Konu | Karar |
|---|---|---|
| 1 | Veri | Faz 0'da `data/CLAUDE.md` ile FX/altın verisi kontrol edilir |
| 2 | MA gün sınırı | Ana: TR 00:00; sağlamlık: NY 17:00 |
| 3 | MB hareketli ortalama | VWMA(21) ve SWMA(26,5) iki varyant |
| 4 | MC stop filtresi | %0.5 ve %1 iki varyant |
| 5 | MF kapsamı (8 Kasım) | MF de test edilir (MA–MF) |
| 6 | MD giriş (8 Kasım) | MD-a ve MD-b iki varyant |
| 7 | Gün sınırı (8 Kasım, #2'nin yerine) | Ana NY 17:00 (gün + 4S blok), sağlamlık TR 00:00; saat pencereleri TR |
| 8 | MB enstrüman (8 Kasım) | GBPUSD spot ana; EURUSD/USDCAD/USDCHF spot genelleme; AUDUSD/USDJPY spot indirilecek; 6A/6J MB'de yok |

## Tasarım soruları (hepsi yanıtlandı, yukarıda)
1. **Veri:** MA, MB, ME FX/altın verisi istiyor; MC NQ. Hangi FX paritelerinin 15dk/1S/günlük verisi var? (Faz 0'da `data/CLAUDE.md` ile kontrol.)
2. **MA gün sınırı:** TR 00:00 (Monarus'un grafiği, önerilen) mi, NY 17:00 mı (sağlamlık)?
3. **MB hareketli ortalama:** VWMA(21) (yazılı kural, önerilen) mi, SWMA(26,5) (grafikte görünen) mi?
4. **MC stop filtresi:** %0.5 mi, %1 mi, ikisi de varyant mı?
5. **Adım 0 sırası:** MA → MB → ME → MC → MD (önerilen: en ucuz ve iddiası en net olandan başla).
6. MF kapsama alındı; MD girişi MD-a ve MD-b iki varyant (8 Kasım, kullanıcı).
