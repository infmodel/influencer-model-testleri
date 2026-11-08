# Kural kaynakları

Her kuralın Monarus'un (TraderMonarus) hangi videosunun hangi dakikasından alındığı. Linkler videoyu o saniyeden açar.

- **Zaman damgaları ve alıntılar** YouTube'un otomatik Türkçe altyazısından alındı; alıntılar altyazıda birebir geçen haliyle, yazım hatalarıyla birlikte duruyor (örn. "lov" = low, "hay" = high, "Change of" = CHoCH, "marobozu" = marubozu).
- **Kural tanımları** ayrıca Gemini'ye izletilen videoların görüntüsünden netleştirildi. Altyazıda geçmeyip yalnızca ekranda görülen bilgiler "(ekranda, video analizinden)" diye belirtildi; bu satırlarda alıntı yok, dakika video analizindeki işaretten.
- Altyazıda doğrulanamayan ya da satır kırılması yüzünden tek satırda yer almayan ifadeler için alıntı hücresinde "—" var.
- Videolarda sayısal karşılığı olmayan yerlerin nasıl kodlandığı [`karar_gunlugu.md`](karar_gunlugu.md)'de kayıtlı.
- "Kod değil iddia" yazan bölümler (R3, R10, R16, R22, R25) test edilen iddiaların nerede söylendiğini kaydeder; kural değil, karşılaştırma ölçütüdür.

## Özet

| Kod | Kural | Nasıl kodlandı |
|---|---|---|
| [R1](#r1) | Grafik saati (UTC+3, TR) ve günlük / 4S mum sınırı | Ana test NY 17:00 gün sınırı (TradingView FXCM mumları seansa hizalı), sağlamlık TR 00:00; saat pencereleri TR saati. |
| [R2](#r2) | Günlük bias durum tablosu (flow, CRT, inside / kararsız) | MA durum sınıflandırması (flow, CRT, inside, kararsız, dışarıda kapanışlı outside), D+1 hedefe değme. |
| [R3](#r3) | MA iddiası: bias isabeti rakamları | Hedefe değme oranı (bias yönünde D+1'in bias mumunun ucuna değmesi) + ayna kontrolü (aynı mesafede ters yöndeki seviyeye değme oranı). |
| [R4](#r4) | MA-T: 1 saatlik giriş | MA-T olay çalışması: D+1'de 09:00 TR sonrası, önceki günün Fib 0.5 ucuz / pahalı tarafı, 1S gövde kapanışı konfirmesi, min RR 1.8, giriş en geç 19:00 TR. |
| [R5](#r5) | ME-1: günlük bias, 4S CRT girişi | ME-1: bias'lı günde 4S CRT (mumlar 04 / 08 / 12 / 16), 2. mum kapanışında market, stop 2. mum ucu, TP günlük hedef; bias'sız 4S CRT negatif kontrol (ME-1n). |
| [R6](#r6) | ME-2: haftalık bias, günlük CRT girişi | ME-2: haftalık bias → günlük CRT; ertesi gün açılışında market; stop CRT ucu; TP haftalık hedef. |
| [R7](#r7) | MF: haftalık bias | MF: haftalık gövde kapanışı önceki haftanın high'ının üstünde ise yalnız long, low'unun altında ise yalnız short; birkaç pip tolerans parametresi; kararsız haftada ana varyantta işlem yok (MF-1), ikincil varyant önceki yönde devam (MF-1k). |
| [R8](#r8) | MF: günlük tetik (PDH / PDL), 30-35 pip iptali, en fazla 2 deneme | Long'da PDL, short'ta PDH alınması (fitil yeterli); sweep, PDH/PDL'nin 30-35 pip ötesine geçerse o gün işlem yok (sağlamlık: ATR eşdeğeri); kurulum başına en fazla 2 deneme. |
| [R9](#r9) | MF: 15 dakikalık CHoCH girişi, stop ve hedef | 15dk CHoCH seviyesi (sweep tepesindeki mumlardan önceki mumun ucunu geçemeyenin ters ucu; sağında daha uç fitil varsa o fitil) aşılınca market; stop sweep fitili; TP en yakın 15dk swing likiditesi. |
| [R10](#r10) | MF iddiası: win rate aralığı | Kod değil iddia: MF sonuçları bu aralıkla karşılaştırılır. |
| [R11](#r11) | MB: enstrüman, zaman dilimi, işlem saati | MB: GBPUSD spot ana; EURUSD / USDCAD / USDCHF spot genelleme, AUDUSD / USDJPY spot; 15dk; giriş 08:00-18:00 TR. |
| [R12](#r12) | MB: trend filtresi (hareketli ortalama + internal yapı) | Fiyat VWMA(21) üstünde ve son internal kırılım yukarı ise yalnız long (short simetrik); SWMA(26,5) ikinci varyant. |
| [R13](#r13) | MB: marubozu tanımı, limit giriş, 10 mum penceresi | Long için marubozu O = L (short için O = H); 15dk; marubozu açılışına limit; marubozu kapandıktan sonra 10 mum içinde dolmazsa iptal. |
| [R14](#r14) | MB: stop yeri ve en fazla 20 pip | Stop son internal swing ucunun 1-2 pip ötesi; stop mesafesi > 20 pip ise işlem yok; hemen ötede dolmamış FVG varsa ikincil varyant (MB-1F). |
| [R15](#r15) | MB: hedef her zaman 1:1 | TP = 1R sabit; zaman çıkışı yok. |
| [R16](#r16) | MB iddiaları ve kendi çekinceleri | Kod değil iddia: MB sonuçları bu iddialarla karşılaştırılır (3 paritede win rate >= %75; 17 işlemde %88.24). Anlatılan 17 işlemlik dönem (1 Aralık 2025 - 16 Ocak 2026) 2026'ya taşıyor; testte 2026 kullanılmadı. |
| [R17](#r17) | MB'de sayım dışı bırakılan ya da farklı sayılan işlemler | 18:00 sonrası giriş yok, 10 mumdan geç dolum ve 20 pip üstü stop işlem dışı; geri çekilme bacağı marubozuları ikincil varyant. |
| [R18](#r18) | MD: POI = en güncel doldurulmamış 1G / 4S FVG | MD: POI en güncel doldurulmamış 1G veya 4S FVG; eski FVG kullanılmaz (tazelik penceresi parametresi); 1G FVG'ye giderken 4S'te ters yönlü yeni FVG olmamalı. |
| [R19](#r19) | MD: tetik (30dk sweep) ve giriş (kırılım kapanışı ya da FVG retest) | MD-a: POI içinde 30dk iç tepe / dip sweep, sonra kırılım (MSB) mumunun 30dk kapanışında market; MD-b: kırılımın bıraktığı 30dk FVG retest limiti. Sweep sonrası aynı türde yeni 30dk pivot onaylanırsa kurulum düşer. |
| [R20](#r20) | MD: hedef ve en az 1.8R | TP 30dk en yakın karşı swing likiditesi (pivot uzunluğu parametre); karşıda ters 4S FVG varsa içindeki ilk likidite; hedef 1.8R vermiyorsa işlem yok (ablation MD-n1: 1.8R filtresiz). |
| [R21](#r21) | MD: forex saat kuralı (09:00-17:00) | FX'te konfirme 09:00-17:00 TR (17:00 kapanışı dahil); sonrası ertesi gün; ablation 17:00 kuralsız. |
| [R22](#r22) | MD iddiaları (backtest, win rate, aylık R) | Kod değil iddia: MD sonuçları bu iddialarla karşılaştırılır. |
| [R23](#r23) | MD kapsam beyanları | Kodlanamadı: '%20 inisiyatif' ve açıklanmayan kurallar kapsam dışı. Bu bir kapsam notu olarak kayıtlı; iddianın test edilemeyen kısmı olarak sunulmuyor. |
| [R24](#r24) | MC: NQ 15dk açılış sonrası sweep modeli | NQ 15dk, 09:30 NY sonrası 13:00'e kadar; en az 2 mumun ucunu süpürme; A: CISD gövde kapanışı, B: engulf + gövdeye limit; stop sweep ucu; TP 1.5R; BE'li / BE'siz iki varyant; stop mesafesi fiyatın %0.5 / %1'inden büyükse işlem yok. |
| [R25](#r25) | MC iddiası: ay ay TP / stop sayımı | Kod değil iddia: sayımlar 2026 dönemine ait olduğundan testte kullanılmadı (2026 kilitli OOS); yalnızca iddia olarak kayıtlı. |

## R1

**Grafik saati (UTC+3, TR) ve günlük / 4S mum sınırı.**

**Kodda:** Ana test NY 17:00 gün sınırı (TradingView FXCM mumları seansa hizalı), sağlamlık TR 00:00; saat pencereleri TR saati.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [Uzd_Yo4qjr8](https://www.youtube.com/watch?v=Uzd_Yo4qjr8) 20 Yıllık Backtestte %75 Win Rate! Günlük Bias Nasıl Belirlenir? | [15:36](https://www.youtube.com/watch?v=Uzd_Yo4qjr8&t=936s) | Forex'te işlem baktığı saatleri duvar saatiyle veriyor (sabah 9'dan akşam 7'ye kadar); grafik saat dilimi aşağıdaki ekran satırında. | "sabah saat 9'da ekranımıza oturacağız." |
| [aoGMsBR7EEM](https://www.youtube.com/watch?v=aoGMsBR7EEM) HAYATINIZI DEĞİŞTİRECEK TRADE VİDEOSU!! - TÜM DETAYLARIYLA ENTRY MODELLERİM | [09:51](https://www.youtube.com/watch?v=aoGMsBR7EEM&t=591s) | 4S girişlerinde işlem baktığı saatleri sabah 8'den akşam 4'e kadar olarak veriyor. | "saatler sabah 8'den akşam 4'e kadar." |
| [aoGMsBR7EEM](https://www.youtube.com/watch?v=aoGMsBR7EEM) HAYATINIZI DEĞİŞTİRECEK TRADE VİDEOSU!! - TÜM DETAYLARIYLA ENTRY MODELLERİM | [04:58](https://www.youtube.com/watch?v=aoGMsBR7EEM&t=298s) | 4 saatlik mumların açılış saatlerini 8, 12 ve 16 olarak sayıyor. | "saatleri görmüşsünüzdür. Sabah 8, öğlen" |
| [aoGMsBR7EEM](https://www.youtube.com/watch?v=aoGMsBR7EEM) HAYATINIZI DEĞİŞTİRECEK TRADE VİDEOSU!! - TÜM DETAYLARIYLA ENTRY MODELLERİM | [00:02](https://www.youtube.com/watch?v=aoGMsBR7EEM&t=2s) | Videodaki grafikler UTC+3 saat diliminde; 4S mumlar TR saatiyle 04:00, 08:00, 12:00, 16:00. Günlük / 4S mum sınırı sözlü anlatılmıyor, grafikten okunuyor. (ekranda, video analizinden) | — |

## R2

**Günlük bias durum tablosu (flow, CRT, inside / kararsız).**

**Kodda:** MA durum sınıflandırması (flow, CRT, inside, kararsız, dışarıda kapanışlı outside), D+1 hedefe değme.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [Uzd_Yo4qjr8](https://www.youtube.com/watch?v=Uzd_Yo4qjr8) 20 Yıllık Backtestte %75 Win Rate! Günlük Bias Nasıl Belirlenir? | [02:10](https://www.youtube.com/watch?v=Uzd_Yo4qjr8&t=130s) | Flow: günlük gövde önceki günün high'ının (fitil dahil) üstünde kapanırsa ertesi gün long, hedef o mumun kendi high'ı. | "fitilinin de üstünde bir body kapattığı" |
| [Uzd_Yo4qjr8](https://www.youtube.com/watch?v=Uzd_Yo4qjr8) 20 Yıllık Backtestte %75 Win Rate! Günlük Bias Nasıl Belirlenir? | [03:27](https://www.youtube.com/watch?v=Uzd_Yo4qjr8&t=207s) | CRT: önceki günün ucu alınıp içeride kapanırsa hedef CRT mumunun kendi karşı ucu (low). | "low bölgesini hedeflemek bizim için hem" |
| [Uzd_Yo4qjr8](https://www.youtube.com/watch?v=Uzd_Yo4qjr8) 20 Yıllık Backtestte %75 Win Rate! Günlük Bias Nasıl Belirlenir? | [07:25](https://www.youtube.com/watch?v=Uzd_Yo4qjr8&t=445s) | İki ucu alıp gövdeyle içeride kalan gün kararsız; inside (konsolide) gün ile birlikte işlem yok, gövdenin ana mumun dışında kapanması bekleniyor (inside için 06:47 civarı). | "bizim için bu bölgeler kararsız bölge." |
| [EALRnzj_dXk](https://www.youtube.com/watch?v=EALRnzj_dXk) NASIL BİAS BELİRLENİR - MANİPÜLASYONLARI ANLAMAK | [04:08](https://www.youtube.com/watch?v=EALRnzj_dXk&t=248s) | CRT'nin aylık / haftalık / günlük zaman dilimlerinde aynı mantıkla kullanıldığı ve hedefin önceki mumun karşı ucu olduğu anlatılıyor. | "buradaki tepeyi alıp içini de kapatırsa" |

## R3

**MA iddiası: bias isabeti rakamları.**

**Kodda:** Hedefe değme oranı (bias yönünde D+1'in bias mumunun ucuna değmesi) + ayna kontrolü (aynı mesafede ters yöndeki seviyeye değme oranı).

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [Uzd_Yo4qjr8](https://www.youtube.com/watch?v=Uzd_Yo4qjr8) 20 Yıllık Backtestte %75 Win Rate! Günlük Bias Nasıl Belirlenir? | [26:20](https://www.youtube.com/watch?v=Uzd_Yo4qjr8&t=1580s) | Kendi yaptığı indikatörle altın paritesinde günlük bias için 8.000 küsur işlem (gün) saydığını söylüyor (oran: %60.7, 26:33-26:35). | "8.000 küsur tane işlem açmış." |
| [Uzd_Yo4qjr8](https://www.youtube.com/watch?v=Uzd_Yo4qjr8) 20 Yıllık Backtestte %75 Win Rate! Günlük Bias Nasıl Belirlenir? | [26:43](https://www.youtube.com/watch?v=Uzd_Yo4qjr8&t=1603s) | Oranın ne olduğunu açıklıyor: bias'ın ertesi günün hedefine gitme oranı (işlem sonucu olarak değil). | "günün hedefine gitmesi altın paritesinde" |
| [Uzd_Yo4qjr8](https://www.youtube.com/watch?v=Uzd_Yo4qjr8) 20 Yıllık Backtestte %75 Win Rate! Günlük Bias Nasıl Belirlenir? | [27:18](https://www.youtube.com/watch?v=Uzd_Yo4qjr8&t=1638s) | EURUSD için 21 yıllık geçmişte %71.9 oranını okuyor. | "win rate'e sahip Euro paritesinde." |
| [Uzd_Yo4qjr8](https://www.youtube.com/watch?v=Uzd_Yo4qjr8) 20 Yıllık Backtestte %75 Win Rate! Günlük Bias Nasıl Belirlenir? | [26:20](https://www.youtube.com/watch?v=Uzd_Yo4qjr8&t=1580s) | Diğer enstrümanların ekrandaki tablosu: GBPUSD %66.9, AUDUSD %66.8, USDCAD %80.1 (3000 gün), USDCHF %68.3, XAGUSD %66.0, BTC %80.6. (ekranda, video analizinden) | — |

## R4

**MA-T: 1 saatlik giriş.**

**Kodda:** MA-T olay çalışması: D+1'de 09:00 TR sonrası, önceki günün Fib 0.5 ucuz / pahalı tarafı, 1S gövde kapanışı konfirmesi, min RR 1.8, giriş en geç 19:00 TR.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [Uzd_Yo4qjr8](https://www.youtube.com/watch?v=Uzd_Yo4qjr8) 20 Yıllık Backtestte %75 Win Rate! Günlük Bias Nasıl Belirlenir? | [04:02](https://www.youtube.com/watch?v=Uzd_Yo4qjr8&t=242s) | Önceki günün aralığına Fibonacci çekiyor; fiyatın 0.5 bölgesine (ucuz / pahalı taraf) gelmesini bekliyor. Hedef 0.5'ten önce alınırsa o gün işlem yok. | "fiyat 0,5'un üstüne geldiği zaman veya" |
| [Uzd_Yo4qjr8](https://www.youtube.com/watch?v=Uzd_Yo4qjr8) 20 Yıllık Backtestte %75 Win Rate! Günlük Bias Nasıl Belirlenir? | [12:02](https://www.youtube.com/watch?v=Uzd_Yo4qjr8&t=722s) | 1 saatlik konfirme: son high'ı yapan mumun fitilinin altında 1S gövde kapanışı. | "Fiyatın bir saatte zayıflık yapmasını" |
| [Uzd_Yo4qjr8](https://www.youtube.com/watch?v=Uzd_Yo4qjr8) 20 Yıllık Backtestte %75 Win Rate! Günlük Bias Nasıl Belirlenir? | [15:25](https://www.youtube.com/watch?v=Uzd_Yo4qjr8&t=925s) | 09:00'dan önceki konfirmeler sayılmaz (Asya manipülasyona açık); işlem akşam 7'ye kadar aranıyor (15:43 civarı). | "bize gelen hiçbir konfirmeyi ciddiye" |
| [Uzd_Yo4qjr8](https://www.youtube.com/watch?v=Uzd_Yo4qjr8) 20 Yıllık Backtestte %75 Win Rate! Günlük Bias Nasıl Belirlenir? | [24:01](https://www.youtube.com/watch?v=Uzd_Yo4qjr8&t=1441s) | Hedefe en az 1.8R olmayan işlemlere girmiyor; yakınsa konfirme mumuna limit koyuyor. | "1.8 R olmasını istiyorum." |

## R5

**ME-1: günlük bias, 4S CRT girişi.**

**Kodda:** ME-1: bias'lı günde 4S CRT (mumlar 04 / 08 / 12 / 16), 2. mum kapanışında market, stop 2. mum ucu, TP günlük hedef; bias'sız 4S CRT negatif kontrol (ME-1n).

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [aoGMsBR7EEM](https://www.youtube.com/watch?v=aoGMsBR7EEM) HAYATINIZI DEĞİŞTİRECEK TRADE VİDEOSU!! - TÜM DETAYLARIYLA ENTRY MODELLERİM | [10:30](https://www.youtube.com/watch?v=aoGMsBR7EEM&t=630s) | 4S CRT, günlük bias ile aynı yönde olmalı; ters yöndeki yapı alınmaz. | "Günlük piyasamızla aynı" |
| [aoGMsBR7EEM](https://www.youtube.com/watch?v=aoGMsBR7EEM) HAYATINIZI DEĞİŞTİRECEK TRADE VİDEOSU!! - TÜM DETAYLARIYLA ENTRY MODELLERİM | [05:32](https://www.youtube.com/watch?v=aoGMsBR7EEM&t=332s) | "S+" sırası: 1. mum 08:00, 2. mum 12:00, giriş 16:00 mumu. | "S plus kondisyon olarak yakalamak" |
| [aoGMsBR7EEM](https://www.youtube.com/watch?v=aoGMsBR7EEM) HAYATINIZI DEĞİŞTİRECEK TRADE VİDEOSU!! - TÜM DETAYLARIYLA ENTRY MODELLERİM | [06:14](https://www.youtube.com/watch?v=aoGMsBR7EEM&t=374s) | 2. mum kapandığında market emir. Stop 2. mumun (likiditeyi alan) ucunda (stop bilgisi ekranda, video analizinden). | "kapandığı zaman markete basıp TPM" |
| [aoGMsBR7EEM](https://www.youtube.com/watch?v=aoGMsBR7EEM) HAYATINIZI DEĞİŞTİRECEK TRADE VİDEOSU!! - TÜM DETAYLARIYLA ENTRY MODELLERİM | [06:20](https://www.youtube.com/watch?v=aoGMsBR7EEM&t=380s) | Hedef günlüğün karşı ucu (günlük bias hedefi). | "lov'una kadar sürebilirim veya eğer" |

## R6

**ME-2: haftalık bias, günlük CRT girişi.**

**Kodda:** ME-2: haftalık bias → günlük CRT; ertesi gün açılışında market; stop CRT ucu; TP haftalık hedef.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [aoGMsBR7EEM](https://www.youtube.com/watch?v=aoGMsBR7EEM) HAYATINIZI DEĞİŞTİRECEK TRADE VİDEOSU!! - TÜM DETAYLARIYLA ENTRY MODELLERİM | [02:36](https://www.youtube.com/watch?v=aoGMsBR7EEM&t=156s) | İkinci modeli anlatıyor: haftalık bias, günlükte giriş. | "4 saatlik değil haftalık bias belirleyip" |
| [aoGMsBR7EEM](https://www.youtube.com/watch?v=aoGMsBR7EEM) HAYATINIZI DEĞİŞTİRECEK TRADE VİDEOSU!! - TÜM DETAYLARIYLA ENTRY MODELLERİM | [33:38](https://www.youtube.com/watch?v=aoGMsBR7EEM&t=2018s) | Haftalıkta önceki haftanın low'unu alıp içeride kapanış; beklenti sonraki haftada önceki haftanın high'ı. | "lov'unu almış ve içeride kapatmış." |
| [aoGMsBR7EEM](https://www.youtube.com/watch?v=aoGMsBR7EEM) HAYATINIZI DEĞİŞTİRECEK TRADE VİDEOSU!! - TÜM DETAYLARIYLA ENTRY MODELLERİM | [34:07](https://www.youtube.com/watch?v=aoGMsBR7EEM&t=2047s) | Günlükte önceki günün likiditesi alınıp içeride kapanınca market; hedef haftalık hedef. | "içinde kapandığı anda marketimizi basıp" |

## R7

**MF: haftalık bias.**

**Kodda:** MF: haftalık gövde kapanışı önceki haftanın high'ının üstünde ise yalnız long, low'unun altında ise yalnız short; birkaç pip tolerans parametresi; kararsız haftada ana varyantta işlem yok (MF-1), ikincil varyant önceki yönde devam (MF-1k).

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [07:46](https://www.youtube.com/watch?v=97GD3JmuKFs&t=466s) | Haftalık yön kuralı: önceki haftanın low'unun altında gövde kapanışı. | "altında body kapatıyor Bizim tek" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [08:09](https://www.youtube.com/watch?v=97GD3JmuKFs&t=489s) | Kararsız hafta: ne altta ne üstte kapanış; bu durumda riski düşürerek önceki yönde devam etmeyi de anlatıyor (08:20 civarı). | "ne altta kapanma var ne üstte kapanma" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [09:39](https://www.youtube.com/watch?v=97GD3JmuKFs&t=579s) | Önceki haftanın ucunun birkaç pip içinde kalan kapanış da kırılım sayılabilir (anlatımda 1 ya da 2 pip). | "böyle 1 ya da 2 pips" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [16:30](https://www.youtube.com/watch?v=97GD3JmuKFs&t=990s) | Kararsız haftalarda işlem almamayı öneriyor. | "bölgelerde işlem almamak daha karlı" |

## R8

**MF: günlük tetik (PDH / PDL), 30-35 pip iptali, en fazla 2 deneme.**

**Kodda:** Long'da PDL, short'ta PDH alınması (fitil yeterli); sweep, PDH/PDL'nin 30-35 pip ötesine geçerse o gün işlem yok (sağlamlık: ATR eşdeğeri); kurulum başına en fazla 2 deneme.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [03:13](https://www.youtube.com/watch?v=97GD3JmuKFs&t=193s) | Short için önceki günün high'ının (PDH) alınmasını bekliyor. | "baktığımız için bize pdh" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [21:43](https://www.youtube.com/watch?v=97GD3JmuKFs&t=1303s) | Long için tersi: önceki günün low'unun (PDL) alınması. | "tam tersi pdl aldıktan sonra" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [12:46](https://www.youtube.com/watch?v=97GD3JmuKFs&t=766s) | Likiditesi alınan seviyenin 30 pip ötesine gidilirse trendin döndüğünü düşünmeye başlanabileceğini söylüyor; 30-35 bandına kadar sorun yok (13:04), 40-45 pip ötesinde pozisyonu bırakmayı öneriyor (13:09-13:24). | "likiditesi alınan bölgenin 30 pips" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [13:28](https://www.youtube.com/watch?v=97GD3JmuKFs&t=808s) | 30-35 pip bandında her işlem için kendine iki stop hakkı tanıyor. | "Ben her işlemde kendime iki stop" |

## R9

**MF: 15 dakikalık CHoCH girişi, stop ve hedef.**

**Kodda:** 15dk CHoCH seviyesi (sweep tepesindeki mumlardan önceki mumun ucunu geçemeyenin ters ucu; sağında daha uç fitil varsa o fitil) aşılınca market; stop sweep fitili; TP en yakın 15dk swing likiditesi.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [04:25](https://www.youtube.com/watch?v=97GD3JmuKFs&t=265s) | Giriş zaman dilimi 15 dakika, bazen 5 dakika. | "benim için 15 dakika bazı durumlarda 5" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [15:02](https://www.youtube.com/watch?v=97GD3JmuKFs&t=902s) | CHoCH seviyesinin tanımı: tepe yapan mumun low'u; sağında engel (fitil) varsa seviye o fitile kaydırılıyor (15:05). | "of karakterimiz bunun lowu olmuş oluyor" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [15:27](https://www.youtube.com/watch?v=97GD3JmuKFs&t=927s) | Fitille kırılım yeterli; market ya da limit. | "buradan direkt Market atın isterseniz" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [06:39](https://www.youtube.com/watch?v=97GD3JmuKFs&t=399s) | Teorik hedef önceki günün karşı ucu; pratikte en yakın swing likiditesi. | "en yakın ilk böyle swing likiditeye TP" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [05:30](https://www.youtube.com/watch?v=97GD3JmuKFs&t=330s) | Stop, PDH/PDL'yi alan hareketin en uç fitilinde. (ekranda, video analizinden) | — |

## R10

**MF iddiası: win rate aralığı.**

**Kodda:** Kod değil iddia: MF sonuçları bu aralıkla karşılaştırılır.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [15:59](https://www.youtube.com/watch?v=97GD3JmuKFs&t=959s) | Sistemin win rate'ini %68 ile %80 bandında veriyor. | "Win rate % 68 ve 80 bandında" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [16:47](https://www.youtube.com/watch?v=97GD3JmuKFs&t=1007s) | Kararsız bölgelerde işlem almazsa win rate'in 80-85 bandına çıkacağını söylüyor. | "yaparsanız da Win rate iniz 80 85" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [12:06](https://www.youtube.com/watch?v=97GD3JmuKFs&t=726s) | Paylaştığı bilginin (30 pip sınırı) dayanağı olarak kendi tuttuğu verileri gösteriyor. | "size tuttuğum verilerden" |
| [97GD3JmuKFs](https://www.youtube.com/watch?v=97GD3JmuKFs) Fon Yönetirken Stratejisi Olmayanlara Özel Trade Sistemi | [24:24](https://www.youtube.com/watch?v=97GD3JmuKFs&t=1464s) | Kararsız hafta filtresine 'ince trik' diyor. | "bandında videodaki bahsettiğim İnce trik" |

## R11

**MB: enstrüman, zaman dilimi, işlem saati.**

**Kodda:** MB: GBPUSD spot ana; EURUSD / USDCAD / USDCHF spot genelleme, AUDUSD / USDJPY spot; 15dk; giriş 08:00-18:00 TR.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [00:56](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=56s) | Modeli yalnızca üç paritede kullandığını söylüyor. | "pariteler sadece ben 3" |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [00:02](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=2s) | Kural kutusunda pariteler GBPUSD, AUDUSD, USDJPY. (ekranda, video analizinden) | — |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [04:32](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=272s) | Giriş zaman dilimi yalnızca 15 dakika. | "ama ben sadece 15 dakikada kullanıyorum." |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [04:00](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=240s) | İşlem açma saati sabah 8'den akşam 6'ya kadar; 6'dan sonra yeni pozisyon önermiyor, açık pozisyon taşınabilir. | "beklediğimiz zaman sabah 8 gibi işlem" |

## R12

**MB: trend filtresi (hareketli ortalama + internal yapı).**

**Kodda:** Fiyat VWMA(21) üstünde ve son internal kırılım yukarı ise yalnız long (short simetrik); SWMA(26,5) ikinci varyant.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [07:47](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=467s) | Fiyat ortalamanın altındayken yalnız short'a bakıyor. | "ortalamanın altındayken" |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [07:54](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=474s) | Ortalamanın üstündeyken yalnız long'a bakıyor. | "zaman da sadece longlara bakıyoruz ve" |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [08:07](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=487s) | Ek olarak iç yapıdaki küçük kırılımlara (internal BOS / CHoCH) bakıyor. | "internal yapıdaki internal" |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [00:02](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=2s) | Kural kutusu: 'VWMA 21 üstünde + trend yukarı'. Grafikte ayrıca SWMA (26,5) göstergesi de görünüyor. (ekranda, video analizinden) | — |

## R13

**MB: marubozu tanımı, limit giriş, 10 mum penceresi.**

**Kodda:** Long için marubozu O = L (short için O = H); 15dk; marubozu açılışına limit; marubozu kapandıktan sonra 10 mum içinde dolmazsa iptal.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [4tdq8r8AmvU](https://www.youtube.com/watch?v=4tdq8r8AmvU) Sadece Fitilsiz Mumlarla İşlem Açıyorum | [00:14](https://www.youtube.com/watch?v=4tdq8r8AmvU&t=14s) | Marubozu: giriş yönünün tersi tarafta fitili olmayan mum. | "hiç aşağıda fitil bırakmıyor." |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [02:44](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=164s) | Fiyatın açıldığı gibi anında yukarı ya da aşağı gitmesini istiyor (açılış = uç). | "fiyat açıldığı gibi anında aşağı şey" |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [05:21](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=321s) | Fiyat marubozuya temas edince oradan limit emir. | "limitem emir atıyoruz ve stop noktamızı" |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [03:05](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=185s) | Marubozudan sonra toplam 10 mum içinde fiyatın marubozuya dönüp dokunmasını istiyor. | "totalde 10 tane mum" |

## R14

**MB: stop yeri ve en fazla 20 pip.**

**Kodda:** Stop son internal swing ucunun 1-2 pip ötesi; stop mesafesi > 20 pip ise işlem yok; hemen ötede dolmamış FVG varsa ikincil varyant (MB-1F).

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [8Kdy2v63IJw](https://www.youtube.com/watch?v=8Kdy2v63IJw) My Project for Today: Live, Exact Model Example | [00:29](https://www.youtube.com/watch?v=8Kdy2v63IJw&t=29s) | Stopu son high'ın (short için) birkaç pip üstüne koyuyor. | "bunun 1-2 pips üstüne koyuyorum." |
| [-0lOq-90p6c](https://www.youtube.com/watch?v=-0lOq-90p6c) Stop Mesafem Asla 20 Pipsi Geçmiyor | [00:07](https://www.youtube.com/watch?v=-0lOq-90p6c&t=7s) | Stop mesafesi en fazla 25 pip diyor, kendi tercihi 20 pip. | "maksimum 25 pips ama ben ortalama olarak" |
| [-0lOq-90p6c](https://www.youtube.com/watch?v=-0lOq-90p6c) Stop Mesafem Asla 20 Pipsi Geçmiyor | [00:34](https://www.youtube.com/watch?v=-0lOq-90p6c&t=34s) | Büyük FVG'nin ötesine stop koymak gerekiyorsa işlem almamayı öneriyor. | "yüzden hani böyle büyük FVG'ler olduğu" |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [09:06](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=546s) | Stop seviyesinin hemen ötesinde dolmamış FVG varsa ya işleme girmiyor ya da stopu FVG'nin ötesine koyuyor. | "yani temizlenmemiş veya temas edilmemiş" |

## R15

**MB: hedef her zaman 1:1.**

**Kodda:** TP = 1R sabit; zaman çıkışı yok.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [05:32](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=332s) | Hedefi stop mesafesiyle birebir yazıyor. | "bire bire yazıyoruz." |
| [IyMEvOUwGW0](https://www.youtube.com/watch?v=IyMEvOUwGW0) The Simplest Yet Most Profitable Trading Strategy | [00:17](https://www.youtube.com/watch?v=IyMEvOUwGW0&t=17s) | Marubozuya temastan sonra bire bir alıp çıkıyor. | "bire bir alıp işlemden çıkacağım" |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [00:02](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=2s) | Kural kutusu: 'TP her zaman 1:1'. (ekranda, video analizinden) | — |

## R16

**MB iddiaları ve kendi çekinceleri.**

**Kodda:** Kod değil iddia: MB sonuçları bu iddialarla karşılaştırılır (3 paritede win rate >= %75; 17 işlemde %88.24). Anlatılan 17 işlemlik dönem (1 Aralık 2025 - 16 Ocak 2026) 2026'ya taşıyor; testte 2026 kullanılmadı.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [01:12](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=72s) | Yaptığı backtest'lerde win rate'in %75'in altına düşmediğini söylüyor. | "%75 win rate'in hiç altına düşmedim." |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [01:17](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=77s) | En yüksek aldığı win rate'i %88 olarak veriyor. | "Yani en fazla aldığım win rate de %88." |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [27:20](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=1640s) | 1 Aralık 2025 - 16 Ocak 2026 arası işlem sayısı 17 (15 TP, 2 stop); ekranda %88.24. | "totalli aldığımız işlem sayısı 17" |
| [TClVsd5BkO8](https://www.youtube.com/watch?v=TClVsd5BkO8) 88% Winrate Proof: 45 Days of Real Results | [00:00](https://www.youtube.com/watch?v=TClVsd5BkO8&t=0s) | Shorts kesitinde aynı 17 işlemlik sayım (15 TP, 2 stop). | "ile aldığımız işlem sayısı 17." |
| [QTMJUCQdDF8](https://www.youtube.com/watch?v=QTMJUCQdDF8) I'm trading with an 88% win rate - Here are 3 currency pairs. | [00:19](https://www.youtube.com/watch?v=QTMJUCQdDF8&t=19s) | Shorts kesitinde %75 iddiası. | "%75 win rate'in hiç altına düşmedi." |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [29:08](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=1748s) | Kendi çekincesi: bir yıllık sürede bazı aylarda win rate'in düşebileceğini söylüyor (29:03 civarı: bazı aylarda 65 düşer). | "65 düşer ama ben şu ana kadar ortalama 3" |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [29:23](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=1763s) | Bir yıllık backtest'i bitirmediğini söylüyor. | "bitirmedim ben." |

## R17

**MB'de sayım dışı bırakılan ya da farklı sayılan işlemler.**

**Kodda:** 18:00 sonrası giriş yok, 10 mumdan geç dolum ve 20 pip üstü stop işlem dışı; geri çekilme bacağı marubozuları ikincil varyant.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [26:07](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=1567s) | 18:30 sonrası çıkan kurulumları gerçekçi olması için saymadığını söylüyor. | "çalışmış ama gerçekçi olması için" |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [21:41](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=1301s) | 10 mumdan sonra gelen teste girmeyi önermiyor (11. muma küçük tolerans, 21:35). | "sonra fiyat test ederse tavsiye etmem." |
| [-0lOq-90p6c](https://www.youtube.com/watch?v=-0lOq-90p6c) Stop Mesafem Asla 20 Pipsi Geçmiyor | [00:36](https://www.youtube.com/watch?v=-0lOq-90p6c&t=36s) | Büyük FVG nedeniyle stop uzayacaksa işlem alınmıyor. | "zaman işlem almayın." |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [22:53](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=1373s) | Gün içinde kârdayken geri çekilme bacağındaki marubozulara da girilebileceğini anlatıyor. | "bu tarz yapılara girebilirsiniz" |
| [Sk5cLJuGe1E](https://www.youtube.com/watch?v=Sk5cLJuGe1E) 88.24% WIN RATE! An Impossible to Lose Trading Strategy with a 1:1 Ratio. | [25:17](https://www.youtube.com/watch?v=Sk5cLJuGe1E&t=1517s) | Girmediğini söylediği bir işlemi de toplam sayıma (13 TP 2 stop) kattığını söylüyor. | "girmedim. Bununla da beraber tam 13 TP 2" |

## R18

**MD: POI = en güncel doldurulmamış 1G / 4S FVG.**

**Kodda:** MD: POI en güncel doldurulmamış 1G veya 4S FVG; eski FVG kullanılmaz (tazelik penceresi parametresi); 1G FVG'ye giderken 4S'te ters yönlü yeni FVG olmamalı.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [8YMuoKYoSC4](https://www.youtube.com/watch?v=8YMuoKYoSC4) Bu Hafta Aldığım Tüm İşlemleri Anlatıyorum / +6.2R! | [01:36](https://www.youtube.com/watch?v=8YMuoKYoSC4&t=96s) | Bias için yalnızca son oluşmuş FVG'leri kullanıyor. | "son güncel oluşmuş PVG'lerden" |
| [8YMuoKYoSC4](https://www.youtube.com/watch?v=8YMuoKYoSC4) Bu Hafta Aldığım Tüm İşlemleri Anlatıyorum / +6.2R! | [05:23](https://www.youtube.com/watch?v=8YMuoKYoSC4&t=323s) | Geçmişteki FVG'leri çok kullanmadığını, güncel olanlara baktığını söylüyor (5-10 gün önceki FVG: 04:57). | "geçmişteki FVG'leri çok" |
| [pchmmbx1qnU](https://www.youtube.com/watch?v=pchmmbx1qnU) Explaining All the Trades I Took This Week / +6.45R! | [02:48](https://www.youtube.com/watch?v=pchmmbx1qnU&t=168s) | Günlükte son oluşan FVG'ye temasa bakıyor. | "Son güncel FVG'mize." |
| [8YMuoKYoSC4](https://www.youtube.com/watch?v=8YMuoKYoSC4) Bu Hafta Aldığım Tüm İşlemleri Anlatıyorum / +6.2R! | [05:47](https://www.youtube.com/watch?v=8YMuoKYoSC4&t=347s) | 1G FVG'ye giderken 4S'te ters yönde FVG oluşmamış olması ayrıca aranıyor. | "4H'ta FVG yapmamış." |

## R19

**MD: tetik (30dk sweep) ve giriş (kırılım kapanışı ya da FVG retest).**

**Kodda:** MD-a: POI içinde 30dk iç tepe / dip sweep, sonra kırılım (MSB) mumunun 30dk kapanışında market; MD-b: kırılımın bıraktığı 30dk FVG retest limiti. Sweep sonrası aynı türde yeni 30dk pivot onaylanırsa kurulum düşer.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [8YMuoKYoSC4](https://www.youtube.com/watch?v=8YMuoKYoSC4) Bu Hafta Aldığım Tüm İşlemleri Anlatıyorum / +6.2R! | [02:09](https://www.youtube.com/watch?v=8YMuoKYoSC4&t=129s) | HTF FVG'ye temasta 30 dakikaya inip bir likidite sweep'i bekliyor. | "likidite swip hareketi bekliyorum ve" |
| [pchmmbx1qnU](https://www.youtube.com/watch?v=pchmmbx1qnU) Explaining All the Trades I Took This Week / +6.45R! | [03:24](https://www.youtube.com/watch?v=pchmmbx1qnU&t=204s) | Sweep'ten sonra 'zayıflık' (entry konfirme) ile giriyor; zayıflığın sözlü tanımı yok. | "birlikte zayıflık sonrası işleme dahil" |
| [pchmmbx1qnU](https://www.youtube.com/watch?v=pchmmbx1qnU) Explaining All the Trades I Took This Week / +6.45R! | [01:49](https://www.youtube.com/watch?v=pchmmbx1qnU&t=109s) | GBPUSD'de konfirme gelince marketle girdiğini anlatıyor (17:00 kapanışıyla oluşan konfirme). | "Ben de oralardan marketle işleme dahil" |
| [8YMuoKYoSC4](https://www.youtube.com/watch?v=8YMuoKYoSC4) Bu Hafta Aldığım Tüm İşlemleri Anlatıyorum / +6.2R! | [02:15](https://www.youtube.com/watch?v=8YMuoKYoSC4&t=135s) | Çizimlerde giriş, kırılımda bırakılan 30dk FVG'nin retest'inde (limit / market belirsiz). (ekranda, video analizinden) | — |

## R20

**MD: hedef ve en az 1.8R.**

**Kodda:** TP 30dk en yakın karşı swing likiditesi (pivot uzunluğu parametre); karşıda ters 4S FVG varsa içindeki ilk likidite; hedef 1.8R vermiyorsa işlem yok (ablation MD-n1: 1.8R filtresiz).

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [8YMuoKYoSC4](https://www.youtube.com/watch?v=8YMuoKYoSC4) Bu Hafta Aldığım Tüm İşlemleri Anlatıyorum / +6.2R! | [06:43](https://www.youtube.com/watch?v=8YMuoKYoSC4&t=403s) | Hedefi en yakın likidite bölgesine koyuyor. | "dahil olup en yakın likidite bölgesinde" |
| [8YMuoKYoSC4](https://www.youtube.com/watch?v=8YMuoKYoSC4) Bu Hafta Aldığım Tüm İşlemleri Anlatıyorum / +6.2R! | [07:20](https://www.youtube.com/watch?v=8YMuoKYoSC4&t=440s) | En yakın likiditenin en az 1.8R vermesi gerektiğini söylüyor. | "likiditenin minimum bana 1.8 ar kar" |
| [8YMuoKYoSC4](https://www.youtube.com/watch?v=8YMuoKYoSC4) Bu Hafta Aldığım Tüm İşlemleri Anlatıyorum / +6.2R! | [07:40](https://www.youtube.com/watch?v=8YMuoKYoSC4&t=460s) | En yakın likidite 1.8R'dan düşükse işleme girmemeyi tercih ediyor. | "low bölgesi 1.8Rdan daha düşükse ben" |
| [pchmmbx1qnU](https://www.youtube.com/watch?v=pchmmbx1qnU) Explaining All the Trades I Took This Week / +6.45R! | [03:03](https://www.youtube.com/watch?v=pchmmbx1qnU&t=183s) | Karşıda 4S bullish FVG varsa hedefi onun içindeki 30dk likiditeye koyuyor. | "TP'mi buradaki bullish FVG'nin içinde 30" |

## R21

**MD: forex saat kuralı (09:00-17:00).**

**Kodda:** FX'te konfirme 09:00-17:00 TR (17:00 kapanışı dahil); sonrası ertesi gün; ablation 17:00 kuralsız.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [pchmmbx1qnU](https://www.youtube.com/watch?v=pchmmbx1qnU) Explaining All the Trades I Took This Week / +6.45R! | [01:26](https://www.youtube.com/watch?v=pchmmbx1qnU&t=86s) | Forex'te 17:00'den sonra çıkan konfirmelere girmiyor. | "17.00'dan sonra işlem çıkarsa ben" |
| [pchmmbx1qnU](https://www.youtube.com/watch?v=pchmmbx1qnU) Explaining All the Trades I Took This Week / +6.45R! | [01:32](https://www.youtube.com/watch?v=pchmmbx1qnU&t=92s) | O durumda ertesi günün seans açılışını (sabah 9) bekliyor. | "açılışını bekliyorum. Yani saat sabah" |
| [pchmmbx1qnU](https://www.youtube.com/watch?v=pchmmbx1qnU) Explaining All the Trades I Took This Week / +6.45R! | [01:45](https://www.youtube.com/watch?v=pchmmbx1qnU&t=105s) | 4.30 civarında oluşan, 5 kapanışıyla biten GBP konfirmesine girmiş. | "4.30 civarı işte tam 5 kapanışıyla" |
| [pchmmbx1qnU](https://www.youtube.com/watch?v=pchmmbx1qnU) Explaining All the Trades I Took This Week / +6.45R! | [01:25](https://www.youtube.com/watch?v=pchmmbx1qnU&t=85s) | Kural yalnız forex için; endeks ve gümüşte işlemler 17:00-17:30 arasında açılmış. (ekranda, video analizinden) | — |

## R22

**MD iddiaları (backtest, win rate, aylık R).**

**Kodda:** Kod değil iddia: MD sonuçları bu iddialarla karşılaştırılır.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [8YMuoKYoSC4](https://www.youtube.com/watch?v=8YMuoKYoSC4) Bu Hafta Aldığım Tüm İşlemleri Anlatıyorum / +6.2R! | [08:48](https://www.youtube.com/watch?v=8YMuoKYoSC4&t=528s) | Parite başına minimum 2-3 yıllık backtest yaptığını söylüyor (08:37: parite başı). | "tek 2 senelik 3 senelik" |
| [8YMuoKYoSC4](https://www.youtube.com/watch?v=8YMuoKYoSC4) Bu Hafta Aldığım Tüm İşlemleri Anlatıyorum / +6.2R! | [09:09](https://www.youtube.com/watch?v=8YMuoKYoSC4&t=549s) | 3 yıllık backtest'in %80 win rate çıkmasını varsayımsal örnek olarak veriyor. | "3 yıllık beklestini yap %80 win ratei" |
| [8YMuoKYoSC4](https://www.youtube.com/watch?v=8YMuoKYoSC4) Bu Hafta Aldığım Tüm İşlemleri Anlatıyorum / +6.2R! | [09:12](https://www.youtube.com/watch?v=8YMuoKYoSC4&t=552s) | Aynı cümlede bu sayıları 'sallıyorum' diye belirtiyor. | "olsun. sallıyorum bunları hani ama" |
| [pchmmbx1qnU](https://www.youtube.com/watch?v=pchmmbx1qnU) Explaining All the Trades I Took This Week / +6.45R! | [09:31](https://www.youtube.com/watch?v=pchmmbx1qnU&t=571s) | Ortalama olarak ayda 6-10R kârlılığı iyi buluyor. | "6 6 R 10 R bandında bir karlılık" |
| [U8P0yNSCkuE](https://www.youtube.com/watch?v=U8P0yNSCkuE) Haftalık Değerlendirme ve Soru Cevap | [30:48](https://www.youtube.com/watch?v=U8P0yNSCkuE&t=1848s) | 21 Eylül - 30 Ekim arası 12 işlemde 16R ve %75 win rate. | "tam 16 R kazanmışım win rate'im de %75." |
| [U8P0yNSCkuE](https://www.youtube.com/watch?v=U8P0yNSCkuE) Haftalık Değerlendirme ve Soru Cevap | [29:19](https://www.youtube.com/watch?v=U8P0yNSCkuE&t=1759s) | Ayda 8R kazanmaktan söz ediyor. | "Ayda 8 ar yılda 2x" |
| [U8P0yNSCkuE](https://www.youtube.com/watch?v=U8P0yNSCkuE) Haftalık Değerlendirme ve Soru Cevap | [27:08](https://www.youtube.com/watch?v=U8P0yNSCkuE&t=1628s) | Model oluşunca işlemin %70-80 ihtimalle TP'ye gittiğini söylüyor. | "modelim oluşursa %70-80 ihtimalle o poz" |

## R23

**MD kapsam beyanları.**

**Kodda:** Kodlanamadı: '%20 inisiyatif' ve açıklanmayan kurallar kapsam dışı. Bu bir kapsam notu olarak kayıtlı; iddianın test edilemeyen kısmı olarak sunulmuyor.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [U8P0yNSCkuE](https://www.youtube.com/watch?v=U8P0yNSCkuE) Haftalık Değerlendirme ve Soru Cevap | [23:52](https://www.youtube.com/watch?v=U8P0yNSCkuE&t=1432s) | İşleme girmek için 5-6 sabit kuralı olduğunu söylüyor; kuralların hepsi anlatılmıyor. | "Tamamen kurallara dayalı işte 5-6 tane" |
| [8YMuoKYoSC4](https://www.youtube.com/watch?v=8YMuoKYoSC4) Bu Hafta Aldığım Tüm İşlemleri Anlatıyorum / +6.2R! | [09:57](https://www.youtube.com/watch?v=8YMuoKYoSC4&t=597s) | Sistemin %80 mekanik, %20 küçük kontroller olmasının mantıklı olduğunu söylüyor. | "mekanik %20 de işte böyle hani ufak" |
| [U8P0yNSCkuE](https://www.youtube.com/watch?v=U8P0yNSCkuE) Haftalık Değerlendirme ve Soru Cevap | [13:40](https://www.youtube.com/watch?v=U8P0yNSCkuE&t=820s) | Başka bir yayında modelin %90 mekanik olduğunu söylüyor. | "%90 şey mekanik." |
| [3PGkHwkDZxA](https://www.youtube.com/watch?v=3PGkHwkDZxA) Explaining All the Trades I Took This Week | [07:34](https://www.youtube.com/watch?v=3PGkHwkDZxA&t=454s) | Giriş konfirmasyon kuralını Mart, Nisan, Mayıs'ta çok stop olduktan sonra değiştirdiğini söylüyor (6 ay önceki giriş farklı: 07:28). | "ve Mayıs'ta çok fazla stop olduğum için" |
| [3PGkHwkDZxA](https://www.youtube.com/watch?v=3PGkHwkDZxA) Explaining All the Trades I Took This Week | [07:47](https://www.youtube.com/watch?v=3PGkHwkDZxA&t=467s) | Değişiklik sonrası sistemin daha kârlı olduğunu söylüyor. | "değiştirdim. Ve şu an çok daha karlı," |

## R24

**MC: NQ 15dk açılış sonrası sweep modeli.**

**Kodda:** NQ 15dk, 09:30 NY sonrası 13:00'e kadar; en az 2 mumun ucunu süpürme; A: CISD gövde kapanışı, B: engulf + gövdeye limit; stop sweep ucu; TP 1.5R; BE'li / BE'siz iki varyant; stop mesafesi fiyatın %0.5 / %1'inden büyükse işlem yok.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [22:14](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=1334s) | Likidite sayması için en az iki mumun ucunun alınmasını istiyor. | "derken şey minimum tam iki tane şey" |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [23:45](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=1425s) | Sweep sonrası son swing'in ötesinde kapanış gelince market (CISD). | "buranın üstüne bir kapanış yapmış." |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [21:09](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=1269s) | İkinci yapı: fiyat önceki mumun likiditesini alıp engulf atarsa, engulf edilen mumun gövdesine limit. | "body'sine şey limit atıp" |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [20:28](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=1228s) | Sabit hedef 1.5R. | "Hedefimiz şey 1,5 ar sabit." |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [19:23](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=1163s) | 1R sonrası stop entry (giriş fiyatına çekme) kullanıyor. | "Yani birerden sonra şey stop enterry" |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [21:36](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=1296s) | İşlem baktığı saat aralığını 4.30 ile 8 arası olarak veriyor; ABD açılışının 4.30'ta başladığını söylüyor (24:59). | "Sadece saat şeyden 4.30'tan 8'e şey" |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [104:56](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=6296s) | Stop mesafesi %1'i aşıyorsa girmiyor, %0.5 civarını girilebilir buluyor. | "çoksa dahil olmam. %0,5 yani girilebilir" |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [20:23](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=1223s) | Açılış sonrası likidite alımının tepesinin stop olarak anlatıldığı cümle (altyazı bozuk; stopun yeri bu satırdan kesin okunamıyor). | "sonrası iki fitil tepesi stop." |

## R25

**MC iddiası: ay ay TP / stop sayımı.**

**Kodda:** Kod değil iddia: sayımlar 2026 dönemine ait olduğundan testte kullanılmadı (2026 kilitli OOS); yalnızca iddia olarak kayıtlı.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [159:57](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=9597s) | Mart: 4 TP, 1 stop (BE işlemleri sayım dışı). | "mart ayı da 4 tp bir stop yani sabit şey" |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [146:46](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=8806s) | Nisan: 4 TP, 2 stop. | "4 TP total stop sayısı 2. Nisan ayı" |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [146:49](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=8809s) | Mayıs: 6 TP, 1 stop. | "birazcık düşük geldi. Şey Mayıs ayı 6 TP" |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [96:14](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=5774s) | Haziran: 7 TP, 3 stop (1.5R sabit hedef). | "3 stop sabit şey 1,5 ar aldığımız için 7" |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [54:49](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=3289s) | Temmuz: 6 TP, 3 stop. | "6 TP 3 stop total karlılık" |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [28:40](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=1720s) | Ağustos: 5 TP, 1 stop. | "ayı boyu total 5 TP" |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [31:21](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=1881s) | Stop entry (BE) işlemlerini win rate hesabına dahil etmediğini söylüyor. | "yaparken stop entryyi win rate'e dahil" |
| [Y4UrdYv6dSU](https://www.youtube.com/watch?v=Y4UrdYv6dSU) NQ' da backtest atarak konsept deniyoruz( Soru Cevap ) | [31:36](https://www.youtube.com/watch?v=Y4UrdYv6dSU&t=1896s) | Sayımı 2026'nın tamamı için sürdüreceğini söylüyor. | "2026'nın tamamını bitirip bakalım işte" |
