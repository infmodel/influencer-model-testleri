# Monarus: Gemini (4 Argon) video analizleri, özet notlar

Ham Gemini cevapları kullanıcının Gemini geçmişinde (link her başlıkta). Buradaki notlar Claude'un özetidir. Gemini rakamları ekrandan okuyor; şüpheliler (?) ile işaretli. 2026 tarihli tek tek işlemler Gemini'den özellikle istenmedi (kilitli OOS).

---

## Sk5cLJuGe1E: 88.24% WR, 1:1 marubozu (MB)
- **Enstrüman/TF:** Yalnızca **GBPUSD, AUDUSD, USDJPY** (FXCM verisi), sabit **15dk**. EUR ve altında "verimli değil" denip kullanılmıyor [28:43].
- **Saat:** 08:00–18:00, grafik **UTC+3 (TR)**. 18:00 sonrası yeni işlem yok; açık işlem taşınabilir.
- **Ekrandaki kural kutusu [00:02]:** (1) 3 parite, (2) marubozu sonrası **10 mum içinde** geri gelip marubozu açılışına temas, (3) trend yönünde: **VWMA 21** üstünde + trend yukarı (short simetrik), (4) 08–18, (5) **TP her zaman 1:1**, (6) 15dk.
- **Göstergeler (grafik listesi):** "Market Structure (Choch/BOS) (5)" internal yapı göstergesi (muhtemelen pivot uzunluğu 5 ?), "Open Marubozu ATR (5, 14, 1)", ayrıca "SWMA (26,5)" görünüyor; kural metni VWMA 21 diyor (çelişki ?), "Twin Range Strategy Alpha".
- **Marubozu:** Long için **alt fitil yok** (açılış = low), short için **üst fitil yok** (açılış = high). Sayısal tolerans yok, işaretleme göstergeye bırakılıyor.
- **Giriş:** VWMA ve internal yapıyla aynı yönde BOS/CHoCH yapıp yeni uç oluşturan bacaktaki marubozunun **açılışına limit**. Günün/haftanın ilk işleminde yalnızca **itki bacağındaki** marubozular; gün içinde 1–2R kâr alınmışsa geri çekilme bacağındakiler de serbest.
- **Tetiklenme süresi:** 9–10 mum (11. muma "tolerans").
- **Stop:** son swing low/high'ın **1–2 pip** dışı. Hemen dışında dolmamış FVG varsa stop FVG dışına ya da işlem yok. Tipik 10–15 pip, **maks 20 (esnek 25) pip**. "Son dip" seçimi kısmen sübjektif.
- **Hedef:** sabit **1R**, trailing/parçalı yok.
- **Mekanizma:** Gerekçe verilmedi; başka bir içerik üreticisinden alınıp "konfirme eklenmiş" [00:12].
- **İddia:** AUDUSD 1 Ara 2025–16 Oca 2026: **17 işlem, 15 TP / 2 SL, %88.24** (+13R). Genel: 3 paritede 5–6 aylık backtest, "%70–75'in altına düşmedi", en yüksek %88; 1 yıllık test yok.
- **Sayım dışı bırakılanlar:** 18:00/18:30 sonrası ve gece kurulumları, 10 mumdan geç temaslar, büyük FVG veya >20–25 pip stoplu kurulumlar, ilk işlemde geri çekilme bacağı marubozuları. Girmediği bir işlem backtest'e TP olarak dahil.
- **Maliyet:** dahil değil.
- **Ekrandaki Aralık 2025 AUDUSD işlemleri (IS):** 11 işlem, 10 TP / 1 SL; stop mesafeleri 5.9–13.8 pip. Spot kontrol için kullanılabilir (2026 kısmı kullanılmaz).

---

## Uzd_Yo4qjr8: 20 yıllık backtest, günlük bias + 1S giriş (MA)
- **Enstrümanlar:** GBPUSD, XAUUSD, USDJPY, EURUSD, AUDUSD (FXCM); USDCAD, USDCHF (OANDA); XAGUSD; BTCUSD.P (OKX). TF: **1G** bias/hedef, **1S** giriş. Grafik **UTC+3**, gün ayracı 00:00 TR (?; sözlü değil, grafikten).
- **Günlük bias (PDH/PDL fitilden, kırılım gövde kapanışıyla):**
  - **Flow long:** gövde PDH üstünde kapanır → ertesi gün long, **hedef = bu mumun kendi high'ı**. Short simetrik.
  - **CRT short:** PDH fitille alınır, gövde PDH altında kapanır → ertesi gün short, **hedef = CRT mumunun kendi low'u**. Long simetrik. (CRT mumunun rengi/kapanış yeri belirsiz; çizimde "PDH altında kapanış" yeterli.)
  - **Inside (konsolide):** işlem yok; ana mumun H/L'si dışında gövde kapanışı beklenir.
  - **Kararsız (outside, gövde içeride):** işlem yok; bu mumun H/L'si dışında kapanış beklenir.
  - **Outside + dışarıda gövde kapanışı:** o yönde bias.
- **1S giriş:**
  - Önceki günün (fitilden fitile) Fib 0.5'i. Fiyat 0.5'e değmeden hedefe giderse o gün işlem yok. Long için 0.5 altı (ucuz), short için üstü.
  - **09:00 TR'den önceki 1S konfirmeler sayılmaz** (Asya "manipülasyon").
  - Konfirme (short): yükselişte son high yapan 1S mumun **low'unun altında 1S gövde kapanışı**; yeni high fitili olup üstünde kapanamazsa referans o mum olur. Long simetrik. 1S inside barlar yok sayılır.
  - Giriş market; RR < 1.8 ise konfirme seviyesine limit. **Min RR 1.8.**
  - **Stop:** kırılım öncesi son 1S swing ucunun hemen dışı. **TP:** günlük hedef (PDH/PDL). Gün sonunda TP olmazsa stop girişe çekilebilir.
  - İşlem saatleri 09:00–17/18, en geç 19:00 TR.
- **Mekanizma:** Verilmedi ("fiyat hangi tarafa gitmek istediğini gösterdi"); Asya = manipülasyon; CRT kendi ucunu hedeflemek "daha güvenli".
- **İddia, "Daily Bias" indikatörü (kendi Pine kodu, gösterilmedi):** Yüzdeler **işlem WR'si değil**, "bias yönünde ertesi gün günlük hedefe değme oranı" (kendisi söylüyor [26:21]). 0.5 şartı sayılıyor mu belirsiz. Maliyet yok.

| Enstrüman | Toplam gün | Bias günü | Başarılı | Başarısız | Oran | Konsolide | Kararsız |
|---|---|---|---|---|---|---|---|
| XAUUSD | 8005 | 1877 | 1140 | 737 | %60.7 | 3282 | 1882 |
| EURUSD | 8667 | 4800 | 3453 | 1346 | %71.9 | 1106 | 1380 |
| GBPUSD | 8620 | 4449 | 2977 | 1471 | %66.9 | 1094 | 1559 |
| AUDUSD | 8642 | 4748 | 3172 | 1575 | %66.8 | 1072 | 1409 |
| USDCAD | 3000 | 1466 | 1173 | 292 | %80.1 | 446 | 555 |
| USDCHF | 8612 | 4401 | 3005 | 1395 | %68.3 | 1147 | 1599 |
| XAGUSD | 8060 | 4120 | 2719 | 1400 | %66.0 | 1272 | 1296 |
| BTCUSD.P | 2441 | 1296 | 1044 | 251 | %80.6 | 396 | 384 |

- **Claude notu (hipotez, sonuç değil):** Hedef, bias mumunun kendi ucu, yani ertesi günün bugünkü H'yi (long) aşması. Bu olayın koşulsuz baz oranı yüksek olabilir. Asıl test, oranın **koşulsuz ve ters yönlü baza göre fazlası**. Ayrıca altın tablosunda bias + konsolide + kararsız toplamı (7041) toplam günden (8005) az; tablo tanımı tutarsız (?).

---

## aoGMsBR7EEM: Tüm entry modellerim (ME + MA'nın giriş katmanları)
Ekrandaki kutu [00:02]: **1- Günlük bias → 4H entry, 2- Haftalık bias → 1D entry, 3- Günlük bias → 1H/15M likidite temizliği**; saatler 08.00, 12.00, 16.00. Hepsi UTC+3. Örnekler Eyl–Eki 2025 (IS): AUDUSD, EURUSD, BTCUSDT.P, USDJPY. "Fonda ve kendi kasamda yalnızca bu üç model" [43:23]. Bu yapıları 1–1,5 yıldır kullanıyor.

**Günlük bias (Uzd ile aynı omurga):** Continuation = önceki günün H/L dışında kapanış; CRT = önceki ucu alıp içeride kapanış, hedef CRT mumunun karşı ucu. **Ek kural:** bullish CRT'nin ertesi günü bearish CRT olursa plan iptal edilir, bias short'a döner. Gün içinde CRT ucunun fitille ihlali bias'ı bozmaz; günlük kapanış tersse bias iptal.

### Model 1: Günlük bias → 4S CRT (ME)
- 4S mumlar (TR): 04:00 "CBDR", **08:00** Londra, **12:00** NY/öğle, **16:00**. Forex penceresi 08:00–16:00. BTC'de 07:00'den itibaren her 4S kapanışı.
- **4S CRT:** 2. mum, 1. mumun ucunu fitille alıp 1. mumun aralığı içinde kapanır → **2. mum kapanışında (3. mum açılışı) market**. Yön günlük bias ile aynı olmalı; ters CRT alınmaz.
- **Sıralar:** normal 04→08→giriş 12:00; **"S+"** 08→12→giriş 16:00. 1. mum 04:00 olup 08:00'de giriş veren yapı (likiditeyi 04:00 mumu alıyor) "nadiren, 0.5R" (?).
- **Key Level** (soldaki FVG/OB/HTF likidite): zorunlu değil, WR'yi artırır.
- **Opsiyonel 15d onay:** yapı dar ya da riskliyse 15d'de son swing'in "OB"si ötesinde **gövde kapanışı**, ardından market.
- **Stop:** 2. mumun (likidite alan) ucu, sayısal tampon yok. **TP:** günlük flow likiditesi (günlük H/L ya da 4S swing); yakın likidite yeterli RR veriyorsa orası. Min RR söylenmiyor; örnekler 1.92–3.43R.
- Limit neredeyse hiç kullanılmıyor, hep market.

### Model 2: Haftalık bias → günlük CRT
- Haftalık CRT/continuation, MA mantığının haftalık hali. Haftalık inside mum önceki bias'ı korur.
- Günlükte bias yönünde CRT (önceki günün ucunu alıp içeride kapanış) → ertesi gün açılışında market. Stop CRT mumunun ucu, TP haftalık hedef. Örnek RR 2.22.

### Model 3: Günlük bias → 4S Key Level + 15d/1S likidite temizliği + OB (MD'ye yakın)
- **Saat kuralı yok** ("gece de alın, fark etmez" [37:18]).
- 4S veya üstü **Key Level zorunlu** (örneklerde 4S FVG). Fiyat bölgeye girer, 15d iç yapıda önceki tepe/dibi süpürür, son swing'in ötesinde 15d (dağınıksa 1S) **gövde kapanışı** gelir → market.
- 15d içinde oluşan CRT "anlamsız", yalnızca OB kırılımına bakılıyor.
- **Stop:** süpüren fitilin hemen dışı. **TP:** son swing likiditesi, ya da daha uzaktaki **1S fitilsiz marubozu** ("fiyat buraya gelmeyi sever"). Örnekler 2.79R ve 2R.
- **İddia:** Üç modelde de sayısal WR/backtest yok.

---

## 8YMuoKYoSC4: "Bu hafta +6.2R" (MD, ana model)
Gemini (Argon, 8 Kas 01:5x): (özel sohbet linki kaldırıldı) · Önceki Flash-Lite cevabı ((özel sohbet linki kaldırıldı) atıldı.

- **Enstrüman/TF:** İşlemler USDCHF, GBPUSD (FXCM), BTCUSDT.P (OKX). İzleme listesi: DXY, EURUSD, GBPUSD, USDCHF, USDJPY, AUDUSD, USDCAD, XAUUSD, BTC, ETH. Çift ekran: solda **4S veya 1G**, sağda **30dk**. Grafik **UTC+3**. LTF 15dk/1S de olabilir ("tercihe göre") [06:09].
- **Bias:** Yalnızca **en güncel 1G/4S FVG** (fiyatın son hareketinin bıraktığı). 5–10 gün önceki eski FVG'ler kullanılmaz [01:33, 04:40]. Daily bullish FVG'ye değip model vermeyen fiyat yeni bearish FVG bırakırsa bias short'a döner [04:19]. Daily FVG'ye giden düzeltmede 4S'te ters yönlü yeni FVG olmamalı, 4S'te aynı yönlü güncel FVG destek olur [05:37]. PDH/PDL testi ek kesişim [05:55]. FVG = standart 3 mum boşluğu (sözlü tanım yok, çizimden). Haftalık/aylık FVG rolü yok.
- **Tetik (30dk):** HTF FVG içinde/girerken yakın bir 30dk iç tepenin (short) fitille alınması (ekranda "x") [02:07, 03:11].
- **"Zayıflık"/konfirme:** Sözlü tanım yok ("entry modeli oluştuktan sonra zayıflıkla" [06:35]). Çizimlerde: sweep → yükselişi başlatan son ara dibin aşağı kırılması (MSB/CHoCH) → bu düşüşte bırakılan **30dk FVG'nin retest'i** → giriş [02:15, 03:20, 06:40]. Market/limit belirsiz; giriş kutusu 30dk FVG retest'inde.
- **Stop:** sözlü kural yok; üç işlemde de **sweep yapan 30dk fitilin hemen üstü** [02:15, 03:20, 06:47].
- **Hedef:** 30dk'daki **en yakın karşı likidite** (swing low) [02:18, 07:10]; "hangi likiditeden döneceğini bilmiyorum, ilk likiditede çıkıyorum" [08:20]. Ekran başında değilse spread payı bırakılır [03:26]. **Min 1.8R**: en yakın likidite 1.8R'den azsa işlem yok [07:18]. Ortalama "maks 2.4–2.5R" [07:59]. Kısmi kâr / BE yok.
- **Saat:** Bu videoda katı saat kuralı yok (girişler ~11:00–13:30 TR). (17:00 kuralı pchmm'den beklenir.)
- **Filtreler:** RR ≥ 1.8; HTF temasta LTF modeli yoksa işlem yok; eski FVG yok; **"%80 mekanik / %20 inisiyatif"** (haber, piyasa koşulu, psikoloji) [09:16, 09:52]. Haftada ~2–3 işlem (bazen 0, nadiren 5–6).
- **İddia:** "parite başı minimum 2–3 yıllık backtest", WR'lerine hakim [08:35]; "%80 win rate" örneğini "sallıyorum" diyerek varsayımsal veriyor [09:07]. Ekranda eski paylaşımlar: "20 YILLIK BACKTEST / %75 WIN RATE" thumbnail'ı ve "Tek model, 5 parite / +26 r Backtest" [00:10, 00:38]. İşlem sayısı ve maliyet yok.
- **Mekanik özet (Gemini):** (1) en güncel 1G/4S FVG yönünde bias, FVG'ye temas bekle; (2) 30dk'da FVG içinde iç tepe/dip sweep; (3) ters yönde ara yapı kırılımı + oluşan 30dk FVG retest'inde giriş; (4) stop sweep fitilinin arkası, TP en yakın karşı 30dk likidite; (5) RR < 1.8 ise ya da "%20 filtre" günse işlem yok.
- **Claude notu:** "En yakın likidite", "yakın iç tepe", "ara dip" seçimleri pivot uzunluğuna bağlı; kodlamada pivot parametresi plato ekseni olur. %20 inisiyatif kodlanamaz (kapsam dışı, kaçış yolu değil).

---

## pchmmbx1qnU: "This week +6.45R" (MD, ana model)
Gemini (Argon, 8 Kas ~02:00): (özel sohbet linki kaldırıldı)

- **Enstrüman/TF:** İşlemler GBPUSD (FXCM), US100 (CAPITALCOM), XAGUSD (FXCM); EURUSD ve SPX500 incelenip pas. DXY korelasyon için. Sol 4S/1G, sağ **30dk**, grafik **UTC+3**.
- **Bias/bölge:** 1G veya 4S **"son güncel FVG"** (fiyata en yakın, doldurulmamış 3 mum boşluğu) [02:49]. Forex'te DXY'nin 1G/4S FVG teması ve yapısı destek [02:08]. Karşıda ters yönlü 4S FVG varsa engel/hedef sayılır [03:00]. Haftalık/aylık FVG rolü yok.
- **Tetik/giriş:** HTF FVG'ye temas → 30dk → yakın tepe/dip fitille alınır (sweep) [01:52] → "zayıflık / entry konfirme" (sözlü tanım yok) [03:24]. GBPUSD'de **16:30 mumunun 17:00 kapanışıyla konfirme, market** [01:46]. Çizimlerde sweep sonrası 30dk iç FVG ya da ters yönlü güçlü kapanış. (8YMu'da giriş FVG retest'inde görünüyordu; pchmm'de konfirme kapanışında market → giriş tanımı iki videoda farklı, ikisi varyant.)
- **Stop:** sweep yapan 30dk swing ucunun hemen dışı [05:57]. Ekran başında olsa yapıya göre taşıyabileceğini söylüyor (yönetim, kodlanmaz).
- **Hedef:** 30dk'daki **en yakın karşı likidite**; karşıda ters 4S FVG varsa onun içindeki ilk 30dk likidite [03:03]. Bu videoda sözlü min RR yok (gerçekleşen 1.9R, 2.45R, 2R; 8YMu'da 1.8R kuralı). Kısmi kâr / BE yok.
- **Saat (önemli):** **Forex'te yalnız 09:00–17:00 TR arası konfirme**; 17:00 sonrası işlem yok, ertesi gün 09:00 beklenir [01:17–01:25]. 17:00 kapanışlı konfirme kabul (GBPUSD), 17:00 sonrası konfirme pas (EURUSD) [01:10]. Kural **yalnız forex**; endeks/gümüş 17:00–17:30'da açılmış. Gerekçe verilmedi. Haber kuralı bu videoda yok.
- **Filtreler:** Pullback olmadan sert tek yönlü piyasada model oluşmaz (10–11 gün işlemsiz) [00:21]; LTF modeli yoksa işlem yok, korele enstrümanda oluşan tercih edilir (SPX yerine US100) [03:58].
- **İddia:** 14 günde 3 işlem, broker'da +6.45R, prop hesaplarda +3.45R (gümüş spread'den stop) [06:58]; "2 hafta önce 5 işlem 4 TP 1 SL" [10:31]; **"haftada min 1 işlem, ayda ortalama 6–10R"** [09:30]. Resmî backtest yok. R hesaplarında maliyet düşülmemiş; spread'in prop hesapta stop ettirdiğini kendisi söylüyor [05:44] (maliyet duyarlılığı kanıtı).
- **Mekanik özet (Gemini):** (1) 1G/4S en güncel FVG'ye pullback temas; (2) forex'te 09:00–17:00 TR; (3) 30dk sweep + ters yönde konfirme mum kapanışı → market; (4) stop sweep ucunun dışı; (5) TP en yakın karşı 30dk likidite (ters 4S FVG varsa onun içindeki ilk likidite).

---

## 97GD3JmuKFs: "Fon yönetirken stratejisi olmayanlara özel trade sistemi" (MF adayı: haftalık bias + PDH/PDL + 15dk CHoCH)
Gemini (Argon, 8 Kas ~02:10): (özel sohbet linki kaldırıldı)

- **Enstrüman/TF:** EURUSD, GBPUSD, AUDUSD (FXCM), BTCUSDT.P (OKX). **1H (haftalık) bias → 1G tetik → 15dk giriş** (sözlü olarak bazen 5dk; örneklerin hepsi 15dk). Grafik **UTC+3**.
- **Haftalık bias:** Haftalık mum önceki haftanın **H'si üstünde gövde kapanışı → sonraki hafta yalnız long; L'si altında → yalnız short** [00:40, 02:34, 07:43]. "Hacimli mum" = bu net gövde kapanışı; hacim göstergesi yok [00:40, 01:33]. 1–3 pip içeride kalan kapanış da kırılım sayılır [09:24, 17:03].
- **Kararsız hafta:** gövde, yön belirleyen son mumun aralığı içinde kalır (fitille uç alınmış olsa da) [01:49, 08:05]. Seçenekler: önceki yönde devam / riski 0.5R'ye indir / işlem yok. **"İnce trik"** = kararsız haftada işlem almamak; WR'yi %68'lerden %80–85'e çıkardığını iddia ediyor [16:02, 24:26]. BTC'de sıkışmada işlem yok [22:14].
- **Günlük tetik:** Long bias → **PDL'nin alınması**, short → **PDH** [00:50, 03:18]. Alarm; günlük kapanış beklenmez, temasta 15dk'ya inilir [04:09, 12:16]. Haftada sabit sınır yok; her yeni günün PDH/PDL'si yeni tetik [03:28, 19:13].
- **İptal (30 pip kuralı):** PDH/PDL alındıktan sonra fiyat **30–35 pip'ten fazla** ileri giderse o gün o seviyeden ters işlem yok [12:47, 13:10]. Bant içindeyse kurulum başına **en fazla 2 deneme (2 stop)** [13:26, 18:36].
- **Giriş (15dk CHoCH):** Short: PDH alındıktan sonra tepedeki mumlardan önceki mumun H'sini geçemeyenin **low'u** CHoCH seviyesi; sağında (kırılımdan önce) daha uçta bir fitil varsa seviye o fitile kaydırılır [14:40, 10:51, 15:02]. **Fitil ihlali de kırılım sayılıyor** (gövde şartı belirsiz) [15:27]. CHoCH çok uzaksa iç yapıda low + pullback + **internal BOS**, kırılımda ya da retest'te giriş [05:40, 20:37]. Çoğunlukla **market**, bazen limit [06:07]. Kendi "mum yapılarını" anlatmıyor [04:40].
- **Stop:** PDH/PDL'yi alan hareketin **en uç fitili**, tampon belirsiz [05:30, 23:16].
- **Hedef:** Teorik hedef karşı günlük likidite (PDL/PDH), pratikte **en yakın anlamlı 15dk swing likiditesi** (WR için) [06:24–07:03]; çok yakın ufak swing R vermiyorsa bir sonraki [11:10]. Alternatif: ilk likiditede %50 kapat, stop girişe, kalan sonraki likiditeye [21:13]. Min RR söylenmiyor (örnekler 1.8–3.6R).
- **Saat:** Kural yok.
- **İddia:** WR **"%68–80"**, kararsız hafta filtresiyle **"%70/80–85"** [16:02, 24:26]; "fonu 1–1.5 ayda geçme" [24:37]. Dayanak "tuttuğum veriler" [05:09, 12:03]; dönem, işlem sayısı, maliyet yok. Örnekler "yakın zamandan seçilmiş".
- **Mekanik özet (Gemini):** (1) haftalık gövde kapanışı önceki haftanın H/L dışında → o yönde bias, kararsız hafta → pas (ya da 0.5R); (2) long'da PDL, short'ta PDH ilk kez alınınca 15dk'ya in; (3) PDH/PDL'den 30–35 pip ötesi → iptal, bant içinde en fazla 2 deneme; (4) 15dk CHoCH (önceki mumun ucunu geçemeyen uç mumun ters ucu; sağda fitil engeli varsa o) kırılımında market, uzaksa internal BOS; (5) stop sweep fitilinin ucu, TP en yakın swing likidite (ya da %50 + BE).
- **Claude notu:** Bu, MA (günlük bias) ve MD'den (FVG + 30dk) ayrı, **en kodlanabilir** ana-model varyantı: tüm bileşenler (haftalık kapanış, PDH/PDL, pip bandı, CHoCH tanımı) sayısal. 30 pip mutlak değer ölçeğe bağlı (pariteler arası ve yıllar arası farklı); ATR'ye göre normalize edilmiş eşdeğeri sağlamlık varyantı olur. Kapsama alınması kullanıcı kararı (seçim MA–ME idi).
