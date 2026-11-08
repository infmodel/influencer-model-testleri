# Kural kaynakları

Her kuralın Dreyko'nun hangi videosunun hangi dakikasından alındığı. Linkler videoyu o saniyeden açar.

- **Zaman damgaları ve alıntılar** YouTube'un otomatik Türkçe altyazısından alındı; alıntılar altyazıda birebir geçen haliyle, yazım hatalarıyla birlikte duruyor (örn. "immersion" = inversion, "esar" = S/R).
- **Kural tanımları** ayrıca Gemini'ye izletilen videoların görüntüsünden netleştirildi ([`kaynaklar/gemini_notlari.md`](kaynaklar/gemini_notlari.md)). Altyazıda geçmeyip yalnızca ekranda görülen bilgiler belirtildi.
- Videolarda sayısal karşılığı olmayan yerlerin nasıl kodlandığı [`karar_gunlugu.md`](karar_gunlugu.md)'de kayıtlı.

## Özet

| Kod | Kural | Nasıl kodlandı |
|---|---|---|
| [R1](#r1) | İşlem saati ve enstrüman | Tüm olaylar 09:30'dan sonra; NQ'da kural kuruldu, ES'de aynen çalıştırıldı; 1 dk bar |
| [R2](#r2) | First Presented FVG tanımı | `events.first_fpfvg`: üçlünün ilk barı ≥09:31 |
| [R3](#r3) | FPFVG destek/direnç, retestte giriş | H1: FPFVG'nin yakın kenarına limit emir |
| [R4](#r4) | FPFVG'nin geçerlilik süresi | İki pencere: A (retest ≤11:10), B (retest ≤10:10) |
| [R5](#r5) | 09:30 öncesi likidite | Açılış öncesi range = 08:00–09:29 high/low |
| [R6](#r6) | 09:30 manipülasyonu (sweep) | H2/H2b tetiği: range ucunun 09:30–09:59 arasında süpürülmesi |
| [R7](#r7) | IFVG | H2: süpürme bacağındaki FVG'nin body kapanışıyla ters kırılması |
| [R8](#r8) | Turtle Soup + CISD | H2b: uca ikinci gidiş (TS), ardışık karşı mumların ilkinin açılışı ötesinde kapanış (CISD) |
| [R9](#r9) | SMT (NQ–ES) | SMT filtresi: karar anına kadar iki endeksten yalnız birinin açılış öncesi ucu alması |
| [R10](#r10) | "3 şart" | Seçicilik turu: F1 (A+ seviye süpürmesi) + SMT |
| [R11](#r11) | Makro saatleri | Makro filtresi: giriş 09:50–10:10 arası |
| [R12](#r12) | Stop | Stop: FVG'yi yaratan bacağın / süpürmenin / TS'nin ucu + 1 tick |
| [R13](#r13) | Hedef | Hedef L: 08:00–09:30 range'inin karşı ucu (ayrıca sabit 2R) |
| [R14](#r14) | A+ seviyeleri | Seçicilik turu F1/F2: Asya H/L ve önceki gün H/L |
| [R15](#r15) | Asya konsolide / hedefe yakınsa işlem yok | Seçicilik turu F3 (Asya range'i/ATR geçmiş medyanın altında) ve F2 (hedef hâlâ açık) |
| [R16](#r16) | İşlem sıklığı | Test edilen kurallar neredeyse her gün tetikleniyor (bkz. README §4a) |
| [R17](#r17) | Serinin kapsamı (iddia ve sınırları) | Test edilen iddia (README §1); private modeller test kapsamı dışında (README §5) |
| [R18](#r18) | 4 Haziran 2025 canlı işlemi | Kod aynı günü FPFVG short olarak yakalıyor (README §3) |
| [R19](#r19) | "Kendiniz backtest edin" | Bu repo tam olarak bunu yapıyor |

## R1

**İşlem saati ve enstrüman.** 09:30 NY sonrası, NQ ana enstrüman, ES teyit, 1 dk grafik.

**Kodda:** Tüm olaylar 09:30'dan sonra; NQ'da kural kuruldu, ES'de aynen çalıştırıldı; 1 dk bar.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [21:00](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=1260s) | Dreyko işlem almaya çalıştığı saat aralığının 09:30 ile 11:00 arası olduğunu söylüyor. | "9.5 ve 11 arasında genelde işlemimi almaya çalışıyorum" |
| [QMr3DGh8ZyY](https://www.youtube.com/watch?v=QMr3DGh8ZyY) Scalp tradelemek için sadece bir modele ihtiyaç duysaydım.. | [14:02](https://www.youtube.com/watch?v=QMr3DGh8ZyY&t=842s) | Kendi disiplini gereği 09:30 sonrasında işlem almayı tercih ettiğini söylüyor. | "ben 9.30 sonrası trade'lemeyi sevdiğim" |
| [XeXiuJEYIiU](https://www.youtube.com/watch?v=XeXiuJEYIiU) Model #1 - Scalp Tradelemek İçin Kullanman Gereken Model - EP. 10 | [08:45](https://www.youtube.com/watch?v=XeXiuJEYIiU&t=525s) | Girişi 1 dakikalık grafikte, hızlı karar vererek market buy ile yaptığını anlatıyor (NQ long örneği). | "Burası 1 dakikalık olduğu için" |
| [P90uzJlCF-Q](https://www.youtube.com/watch?v=P90uzJlCF-Q) Model #2 - Find the Direction of the Day at 9:30 · Pattern Recognition Series (Ep.15) | [16:49](https://www.youtube.com/watch?v=P90uzJlCF-Q&t=1009s) | NQ'da işlem aldığını, ES'e yalnızca teyit amaçlı baktığını söylüyor (ES'de işlem almıyor). _(SMT için ES kullanımı: 06:07 satırı R9'da)_ | "ES tarafında işlem almıyorum" |
| [QMr3DGh8ZyY](https://www.youtube.com/watch?v=QMr3DGh8ZyY) Scalp tradelemek için sadece bir modele ihtiyaç duysaydım.. | [21:56](https://www.youtube.com/watch?v=QMr3DGh8ZyY&t=1316s) | SMT durumunda NQ yerine ES'in işlem tarafı seçilebileceğini örnekliyor; yani ES her zaman yalnızca SMT aracı değil. _(P90uz ile çelişkili örnek)_ | "ES tarafını long'lamalıyız" |

## R2

**First Presented FVG tanımı.** 09:30'dan sonra oluşan ilk 1 dk FVG; 09:30 mumunun kendi FVG'si sayılmaz.

**Kodda:** `events.first_fpfvg`: üçlünün ilk barı ≥09:31.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [08:28](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=508s) | FPFVG'yi 09:30'dan sonra oluşan ilk FVG olarak tanımlıyor. | "9,5'tan sonra oluşan ilk Fair Value Gap bizim neymiş? First Presented" |
| [O_H13qPRyI4](https://www.youtube.com/watch?v=O_H13qPRyI4) Endeks Tradelemek için İhtiyacınız Olan Her Şey - 9.30 Manipulation - 1st Presented FVG - Macro' | [15:46](https://www.youtube.com/watch?v=O_H13qPRyI4&t=946s) | 09:30 mumuyla birlikte oluşan FVG'nin FPFVG sayılmadığını söylüyor. | "First presentation değil. Neden? Çünkü burası 9,5'tan sonra oluşmuyor." |
| [O_H13qPRyI4](https://www.youtube.com/watch?v=O_H13qPRyI4) Endeks Tradelemek için İhtiyacınız Olan Her Şey - 9.30 Manipulation - 1st Presented FVG - Macro' | [16:00](https://www.youtube.com/watch?v=O_H13qPRyI4&t=960s) | 09:30 sonrası oluşan ilk FVG'nin önemli olduğunu vurguluyor ('periyod' otomatik altyazı hatası, FVG kastediliyor). | "bizim için 9,5'tan sonra oluşan ilk periyod önemli" |
| [KDsDDr3FSP4](https://www.youtube.com/watch?v=KDsDDr3FSP4) ICT Macro' Nasıl Tradelenir? DREYKO ile LiveTrading · Manipulation Series (Ep.15) | [02:35](https://www.youtube.com/watch?v=KDsDDr3FSP4&t=155s) | Canlı işlemde 09:30 civarındaki FVG'yi FPFVG saymıyor, henüz FPFVG oluşmadığını söylüyor. | "Buradaki 9,5 gibi sayılmaz" |
| [QMr3DGh8ZyY](https://www.youtube.com/watch?v=QMr3DGh8ZyY) Scalp tradelemek için sadece bir modele ihtiyaç duysaydım.. | [22:48](https://www.youtube.com/watch?v=QMr3DGh8ZyY&t=1368s) | Örnek günde 1dk FPFVG'nin 09:33'te oluştuğunu gösteriyor (ES, 15 dk low risk buy ile birlikte). | "9.33'te oluşmuş first present fair value gap'i" |

## R3

**FPFVG destek/direnç, retestte giriş.** FPFVG günün gerçek S/R'si; retestte, limit emirle giriş.

**Kodda:** H1: FPFVG'nin yakın kenarına limit emir.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [11:35](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=695s) | FPFVG'yi gerçek direnç (destek/direnç) bölgesi olarak tanımlıyor. | "burası gerçek bir resistance, direnç bölgesi" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [11:51](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=711s) | 09:30 manipülasyonu sonrası oluşan FPFVG'nin kırılması ya da tepki alması yönü belirler diyor ('esar' otomatik altyazı hatası olabilir). | "Bu aslında bizim gerçek esarımızdır" |
| [O_H13qPRyI4](https://www.youtube.com/watch?v=O_H13qPRyI4) Endeks Tradelemek için İhtiyacınız Olan Her Şey - 9.30 Manipulation - 1st Presented FVG - Macro' | [16:16](https://www.youtube.com/watch?v=O_H13qPRyI4&t=976s) | FPFVG üstündeki fiyat hareketini alış, altındakini satış tarafına ileten referans olarak tanımlıyor. | "buranın üstündeki fiyat hareketleri fiyatı buyda" |
| [P90uzJlCF-Q](https://www.youtube.com/watch?v=P90uzJlCF-Q) Model #2 - Find the Direction of the Day at 9:30 · Pattern Recognition Series (Ep.15) | [14:41](https://www.youtube.com/watch?v=P90uzJlCF-Q&t=881s) | Girişini low risk sell/FVG retestlerinden yaptığını söylüyor. | "low risk sell veya fair value gap'lerden girmeye çalışan bir trader'ım" |
| [P90uzJlCF-Q](https://www.youtube.com/watch?v=P90uzJlCF-Q) Model #2 - Find the Direction of the Day at 9:30 · Pattern Recognition Series (Ep.15) | [10:24](https://www.youtube.com/watch?v=P90uzJlCF-Q&t=624s) | FPFVG'deki wick için çektiği Fibonacci'nin 0 noktasına gelen fiyatın yeniden satış yediğini gösteriyor (kenar/0 seviyesi tepkisi). _(kısa alıntı satır kesiti; bağlam 10:20-10:26)_ | "Fiyat buradaki 0 noktasına geliyor ve" |
| [KDsDDr3FSP4](https://www.youtube.com/watch?v=KDsDDr3FSP4) ICT Macro' Nasıl Tradelenir? DREYKO ile LiveTrading · Manipulation Series (Ep.15) | [07:40](https://www.youtube.com/watch?v=KDsDDr3FSP4&t=460s) | Canlı işlemde FPFVG oluşmadan/oluşurken limit satış emri koyuyor. | "Şöyle limit sat" |
| [NdIyXxFH7s0](https://www.youtube.com/watch?v=NdIyXxFH7s0) How to Determine A+ Liquidity? Asia Range Model · Manipulation Series (Ep.13) | [03:25](https://www.youtube.com/watch?v=NdIyXxFH7s0&t=205s) | 3dk IFVG'nin EQ (0.5) noktasına wick'le saygı gösterilmesini giriş tetiği olarak gösteriyor ('immersion' = inversion, altyazı hatası). _(FPFVG değil IFVG için EQ girişi)_ | "EQ noktasına yani immersion fapin EQ noktasına respectliyor" |
| [NPKjTTcsEME](https://www.youtube.com/watch?v=NPKjTTcsEME) Range Manipülasyonu Nasıl Kullanılır? · Manipulation Series (Ep.4) | [06:02](https://www.youtube.com/watch?v=NPKjTTcsEME&t=362s) | FVG içinde 0.25 / 0.5 (EQ) / 0.75 seviyelerinde tepki beklediğini söylüyor. _(HTF haftalık FVG bağlamı, 1dk FPFVG değil)_ | "0.25 0,5 seviyesi yani fvg iq seviyesi" |

## R4

**FPFVG'nin geçerlilik süresi.** Sayısal süre verilmiyor; yüksek olasılıklı işlemler 10:50–11:10 makrosunda biter.

**Kodda:** İki pencere: A (retest ≤11:10), B (retest ≤10:10).

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [12:42](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=762s) | 10.50-11.00 makrosuna gelindiğinde günün yüksek olasılıklı işlemlerinin bittiğini söylüyor. _(transkriptte '10.50, 11.00 makrosu' geçiyor, '11:10' değil)_ | "günün high probability dediğimiz en güzel yüksek olasılıklı tradeleri bitiyor" |
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [12:29](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=749s) | FPFVG/ilgili FVG ters yönde fliplenene kadar (kırılana kadar) yönün geçerli olduğunu söylüyor; sayısal süre sınırı verilmiyor. | "Bu fliplenmedikçe düşüş devam edecek" |
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [10:17](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=617s) | FPFVG'ye dönüş hareketinin 09:50-10:10 makrosunda gerçekleştiğini gösteriyor. | "yükseliş 9.50, 10.10 makrosunda gerçekleşmekte" |
| [KDsDDr3FSP4](https://www.youtube.com/watch?v=KDsDDr3FSP4) ICT Macro' Nasıl Tradelenir? DREYKO ile LiveTrading · Manipulation Series (Ep.15) | [08:56](https://www.youtube.com/watch?v=KDsDDr3FSP4&t=536s) | FPFVG'den aldığı pozisyondan 10:00'daki haberden/makrodan önce çıkması gerektiğini söylüyor. _(sayısal geçerlilik süresi bulunamadı)_ | "saat 10 öncesi çıkmam gerekecek makroda" |

## R5

**09:30 öncesi likidite.** 08:00'den itibaren biriken likidite, equal high/low, konsolidasyon.

**Kodda:** Açılış öncesi range = 08:00–09:29 high/low.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [XeXiuJEYIiU](https://www.youtube.com/watch?v=XeXiuJEYIiU) Model #1 - Scalp Tradelemek İçin Kullanman Gereken Model - EP. 10 | [00:30](https://www.youtube.com/watch?v=XeXiuJEYIiU&t=30s) | 09:30 öncesinde düşük dirençli (LRLR) likidite oluşumunu en sevdiği model koşulu olarak söylüyor. | "9.30'dan önce bir low resistance liquidity'nin oluşması" |
| [XeXiuJEYIiU](https://www.youtube.com/watch?v=XeXiuJEYIiU) Model #1 - Scalp Tradelemek İçin Kullanman Gereken Model - EP. 10 | [03:09](https://www.youtube.com/watch?v=XeXiuJEYIiU&t=189s) | LRLR likiditenin saat 08:00'den itibaren oluştuğunu söylüyor (08:00 mumunun low'u). | "burası zaten saat 8 itibarıyla oluşturulmuş" |
| [NdIyXxFH7s0](https://www.youtube.com/watch?v=NdIyXxFH7s0) How to Determine A+ Liquidity? Asia Range Model · Manipulation Series (Ep.13) | [00:33](https://www.youtube.com/watch?v=NdIyXxFH7s0&t=33s) | Asya range'inin net konsolidasyon halinde olmasını istiyor; ardından 09:30'a kadar low resistance yapı arıyor. | "net bir konsolidasyon yapısında bir AS rangei görmek isteriz" |
| [O_H13qPRyI4](https://www.youtube.com/watch?v=O_H13qPRyI4) Endeks Tradelemek için İhtiyacınız Olan Her Şey - 9.30 Manipulation - 1st Presented FVG - Macro' | [04:29](https://www.youtube.com/watch?v=O_H13qPRyI4&t=269s) | Engineering liquidity'yi alınmamış high/low ve eşit tepe/dip olarak tanımlıyor. | "Alınmayan high, alınmayan lowlar, equal high equals lowlar görmek isteriz" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [04:48](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=288s) | 09:30 öncesi fiyatın kendine bir likidite alanı (orijinal konsolidasyon) yarattığını söylüyor. | "9,5 öncesi fiyat kendine bir likit de alanı yaratıyor" |

## R6

**09:30 manipülasyonu (sweep).** 09:30'da range'in bir ucu alınır, sonra fiyat döner.

**Kodda:** H2/H2b tetiği: range ucunun 09:30–09:59 arasında süpürülmesi.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [XeXiuJEYIiU](https://www.youtube.com/watch?v=XeXiuJEYIiU) Model #1 - Scalp Tradelemek İçin Kullanman Gereken Model - EP. 10 | [06:14](https://www.youtube.com/watch?v=XeXiuJEYIiU&t=374s) | 09:30 açılışıyla range high'ın alındığını, ardından hızlı düşüşle range low'un alındığını anlatıyor. | "Range high 9.30 açılışı ile birlikte alınıyor" |
| [XeXiuJEYIiU](https://www.youtube.com/watch?v=XeXiuJEYIiU) Model #1 - Scalp Tradelemek İçin Kullanman Gereken Model - EP. 10 | [05:29](https://www.youtube.com/watch?v=XeXiuJEYIiU&t=329s) | 09:30 manipülasyonunun önce eşit tepeleri aldığını, sonra dönüş yaptığını söylüyor. | "09:30 manipülasyonu ilk buradaki tepeleri alıyor" |
| [O_H13qPRyI4](https://www.youtube.com/watch?v=O_H13qPRyI4) Endeks Tradelemek için İhtiyacınız Olan Her Şey - 9.30 Manipulation - 1st Presented FVG - Macro' | [03:17](https://www.youtube.com/watch?v=O_H13qPRyI4&t=197s) | 09:30 sonrası gerçekleşen hareketlerin manipülasyon olarak değerlendirildiğini söylüyor (karşı taraf likiditesi alınır). | "gerçekleşecek hareketler bizim manipülasyonumuzu oluşturacak hareketlerdir" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [08:35](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=515s) | Turtle soup'un mantığını stop avı sonrası ters dönüş olarak açıklıyor. | "retail'ın köşeye sıkıştırılması ve daha sonra marketin reversal vermesi" |

## R7

**IFVG.** FVG ters yönde body kapanışıyla kırılınca inversion FVG olur, giriş fırsatı.

**Kodda:** H2: süpürme bacağındaki FVG'nin body kapanışıyla ters kırılması.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [12:04](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=724s) | FVG'nin ters yönde fliplenmesine inversion FVG diyor; sonrasında her yapı giriş fırsatı oluyor. | "Fliplendiğini, yani inversion fair value gap olduğunu gözlemliyoruz" |
| [P90uzJlCF-Q](https://www.youtube.com/watch?v=P90uzJlCF-Q) Model #2 - Find the Direction of the Day at 9:30 · Pattern Recognition Series (Ep.15) | [12:04](https://www.youtube.com/watch?v=P90uzJlCF-Q&t=724s) | FVG delinirse (reversal inversion FVG) mevcut pozisyonun kısmi karla kapatılabileceğini söylüyor. _(body kapanışı şartı burada açıkça geçmiyor)_ | "fair value gap eee delinirse yani reversal bearish inversion FVG olursa" |
| [XeXiuJEYIiU](https://www.youtube.com/watch?v=XeXiuJEYIiU) Model #1 - Scalp Tradelemek İçin Kullanman Gereken Model - EP. 10 | [08:17](https://www.youtube.com/watch?v=XeXiuJEYIiU&t=497s) | Fiyat inversion FVG'ye gelip yeni low yapmazsa ilk girişi alıyor (market buy). | "benim için en güçlü konfirmelerden olmalı ve ilk entry'mi buradan almalıyım" |
| [wsTezlpxvP0](https://www.youtube.com/watch?v=wsTezlpxvP0) If I Only Needed One Model to Read the Market.. - DREYKO Mentorship '25 | [22:25](https://www.youtube.com/watch?v=wsTezlpxvP0&t=1345s) | FVG'nin body kapanışıyla kırılmasını inversion FVG teyidi olarak anlatıyor. _(öncelikli listede olmayan video; transkriptte 'inversion' ve 'body' birbirine yakın geçiyor)_ | "diyelim ki kırdı üstünde body kapattı" |

## R8

**Turtle Soup + CISD.** İlk rahatlama rallisinde girilmez; TS sonrası body kapanışıyla CISD.

**Kodda:** H2b: uca ikinci gidiş (TS), ardışık karşı mumların ilkinin açılışı ötesinde kapanış (CISD).

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [07:03](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=423s) | Yeni low ve altında kazanım turtle soup; üstünde body kapanışı breaker/CISD olarak tanımlanıyor. | "burası benim turtle soop'um oluyor ve buranın üstünde body kapanışı breakerım oluyor" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [12:54](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=774s) | Ardışık mumların sertçe geçilmesini CISD olarak tanımlıyor; 'ilk mumun açılışı' ifadesi bu satırda bulunamadı. | "ardışık düşüş veya yükseliş mumları sertçe geçilmesi bizim changing state of deliverimizdir" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [13:02](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=782s) | Seviyenin üstünde body kapanışını CISD sayıyor. | "burasının üstüne body kapatması bizim change ining state of deliveryimizdir" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [06:00](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=360s) | İlk yeşil mumu 'rahatlama rallisi' olarak niteliyor ('ama' altyazı hatası). | "buradaki yeşil mum genelde ama rahatlama rallisi olarak karşımıza çıkıyor" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [07:15](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=435s) | İlk yeşil mum/rahatlama rallisinde hemen girmemeyi söylüyor. | "yeşil mum yaktı diye direkt atlamayın" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [07:44](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=464s) | Rahatlama rallisinde erken inversion FVG girişi yapmanın stop ile sonuçlanacağını söylüyor. | "stop olursunuz. Bunu asla yapmayın" |

## R9

**SMT (NQ–ES).** Bir endeks yeni uç yaparken diğeri yapamaz; "emniyet kemeri".

**Kodda:** SMT filtresi: karar anına kadar iki endeksten yalnız birinin açılış öncesi ucu alması.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [gwF0xk19Gkk](https://www.youtube.com/watch?v=gwF0xk19Gkk) ICT - What is SMT? How to Interpret Correlation? · Manipulation Series (Ep.6) | [04:28](https://www.youtube.com/watch?v=gwF0xk19Gkk&t=268s) | SMT'nin emniyet kemeri işlevi gördüğünü ve stopun SMT'ye güvenerek konduğunu söylüyor ('iin' altyazı hatası). _(öncelikli listede olmayan video (Manipulation Series Ep.6))_ | "Çünkü SMT yapısı bizim iin emniyet kemeri görev" |
| [P90uzJlCF-Q](https://www.youtube.com/watch?v=P90uzJlCF-Q) Model #2 - Find the Direction of the Day at 9:30 · Pattern Recognition Series (Ep.15) | [06:07](https://www.youtube.com/watch?v=P90uzJlCF-Q&t=367s) | SMT: ES yeni high yaparken NQ yapamıyor, NQ tarafı zayıf (short). | "NQ yeni high yapamıyor, Yes yeni high yapıyor" |
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [05:00](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=300s) | Aynı SMT tanımını başka örnekte veriyor. | "ES tarafı higher high yaparken NQ tarafı higher high yapamıyor" |
| [QMr3DGh8ZyY](https://www.youtube.com/watch?v=QMr3DGh8ZyY) Scalp tradelemek için sadece bir modele ihtiyaç duysaydım.. | [24:11](https://www.youtube.com/watch?v=QMr3DGh8ZyY&t=1451s) | SMT'yi bir enstrümanın iç, diğerinin dış likiditeyi alması olarak tanımlıyor. | "ES tarafı iç yapıda manipülasyonu yaparken NQ tarafı dış likiditeye gidiyor" |
| [XeXiuJEYIiU](https://www.youtube.com/watch?v=XeXiuJEYIiU) Model #1 - Scalp Tradelemek İçin Kullanman Gereken Model - EP. 10 | [03:42](https://www.youtube.com/watch?v=XeXiuJEYIiU&t=222s) | SMT örneği: ES Londra low'unu alırken NQ yalnızca 08:00 low'unu alıyor. | "Fakat bizde ise sadece saat 8.00 mumunun low'una gitmekteyiz" |
| [NPKjTTcsEME](https://www.youtube.com/watch?v=NPKjTTcsEME) Range Manipülasyonu Nasıl Kullanılır? · Manipulation Series (Ep.4) | [16:53](https://www.youtube.com/watch?v=NPKjTTcsEME&t=1013s) | SMT'yi çıkış kuralı olarak kullanıyor: NQ range high'ı alıp ES almıyorsa long'dan çık. _(yazılı olmayan, deneyime dayalı kural olduğunu söylüyor)_ | "Es tarafı etmiyor long unuz varsa kesinlikle çıkın" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [17:17](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=1037s) | NQ ve ES arasındaki uyumsuzlukta long pozisyondan çıkma/kar alma önerisi. | "Eğer bir long pozisyondaysanız artık yavaştan çıkmalı" |

## R10

**"3 şart".** HTF key level + SMT + manipülasyon; fazlası sisteme zarar verir.

**Kodda:** Seçicilik turu: F1 (A+ seviye süpürmesi) + SMT.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [XeXiuJEYIiU](https://www.youtube.com/watch?v=XeXiuJEYIiU) Model #1 - Scalp Tradelemek İçin Kullanman Gereken Model - EP. 10 | [02:51](https://www.youtube.com/watch?v=XeXiuJEYIiU&t=171s) | Üç gerekli unsuru sayıyor: HTF key level, SMT, manipülasyon. | "Birincisi high time frame key level, SMT ve manipülasyon" |
| [XeXiuJEYIiU](https://www.youtube.com/watch?v=XeXiuJEYIiU) Model #1 - Scalp Tradelemek İçin Kullanman Gereken Model - EP. 10 | [04:04](https://www.youtube.com/watch?v=XeXiuJEYIiU&t=244s) | Üçten fazlasının sisteme zarar vereceğini söylüyor. | "Fazlası ise sistemine zarar verecek" |
| [XeXiuJEYIiU](https://www.youtube.com/watch?v=XeXiuJEYIiU) Model #1 - Scalp Tradelemek İçin Kullanman Gereken Model - EP. 10 | [04:01](https://www.youtube.com/watch?v=XeXiuJEYIiU&t=241s) | Üçüne birden sahipse smart money'nin ayak izini takip ettiğini söylüyor. | "smart money'nin ayak izlerini takip ediyorsunuz demektir" |

## R11

**Makro saatleri.** 09:50–10:10 ve 10:50–11:10.

**Kodda:** Makro filtresi: giriş 09:50–10:10 arası.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [QMr3DGh8ZyY](https://www.youtube.com/watch?v=QMr3DGh8ZyY) Scalp tradelemek için sadece bir modele ihtiyaç duysaydım.. | [26:59](https://www.youtube.com/watch?v=QMr3DGh8ZyY&t=1619s) | Gerçek makro saatlerinin 09:50-10:10 ve 10:50-11:10 olduğunu söylüyor (ardından lunch makro). | "Gerçek makro saatleri bunlardır. 9.50 10.10 10.50 11.10" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [10:29](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=629s) | Makroyu her saatin son 10 dakikası ve ilk 10 dakikası olarak tanımlıyor. | "son bitiminin son 10 dakikası ile her saatin başlangıcının 10 dakikasını" |
| [O_H13qPRyI4](https://www.youtube.com/watch?v=O_H13qPRyI4) Endeks Tradelemek için İhtiyacınız Olan Her Şey - 9.30 Manipulation - 1st Presented FVG - Macro' | [17:59](https://www.youtube.com/watch?v=O_H13qPRyI4&t=1079s) | 09:30 sonrası makro pencereleri (09:50, 10:50, 11:10 ve 11:50-12:10 civarı) sayılıyor, altyazı bozuk. _(otomatik altyazı bozuk)_ | "makro 950 1050 1110 ve 1150 12 olarak karşımıza çıkıyor" |
| [O_H13qPRyI4](https://www.youtube.com/watch?v=O_H13qPRyI4) Endeks Tradelemek için İhtiyacınız Olan Her Şey - 9.30 Manipulation - 1st Presented FVG - Macro' | [18:39](https://www.youtube.com/watch?v=O_H13qPRyI4&t=1119s) | Manipülasyon anlaşıldıysa makro penceresinin işlem yapılması gereken 20 dakikalık pencere olduğunu söylüyor. | "kesinlikle tradlenmesi gereken 20 dakikalık penceredir" |

## R12

**Stop.** Manipülasyon ucunun ötesi, geniş stop.

**Kodda:** Stop: FVG'yi yaratan bacağın / süpürmenin / TS'nin ucu + 1 tick.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [XeXiuJEYIiU](https://www.youtube.com/watch?v=XeXiuJEYIiU) Model #1 - Scalp Tradelemek İçin Kullanman Gereken Model - EP. 10 | [07:33](https://www.youtube.com/watch?v=XeXiuJEYIiU&t=453s) | Girişi geniş stopla almayı öneriyor. | "ilk entry'mizi alabiliriz. E geniş bir stop olacak şekilde" |
| [P90uzJlCF-Q](https://www.youtube.com/watch?v=P90uzJlCF-Q) Model #2 - Find the Direction of the Day at 9:30 · Pattern Recognition Series (Ep.15) | [13:26](https://www.youtube.com/watch?v=P90uzJlCF-Q&t=806s) | Stopun manipülasyon bölgesinde (ucunda) olduğunu söylüyor. | "burada oluyor veya burada oluyor buradaki manipülasyonda" |
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [08:06](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=486s) | Short girişinin stopunun yukarıdaki manipülasyon seviyesinde olduğunu gösteriyor. _('stop yukarıda' bilgisi görüntüye dayanıyor; yalnızca ses transkripti)_ | "Short'umu alıp artık burası benim Stop'um" |
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [15:38](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=938s) | Dar stop değil, 'güzel' (geniş) stop kullandığını söylüyor. | "küçük dar stop değil. E güzel bir stopla alırım" |

## R13

**Hedef.** 09:30 öncesi range'in karşı ucu, karşı likidite, A+ draw.

**Kodda:** Hedef L: 08:00–09:30 range'inin karşı ucu (ayrıca sabit 2R).

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [XeXiuJEYIiU](https://www.youtube.com/watch?v=XeXiuJEYIiU) Model #1 - Scalp Tradelemek İçin Kullanman Gereken Model - EP. 10 | [05:14](https://www.youtube.com/watch?v=XeXiuJEYIiU&t=314s) | Hedefi 09:30 öncesi eşit tepeler olarak veriyor. | "Buradaki eşit tepelere gitmesini bekleriz" |
| [NdIyXxFH7s0](https://www.youtube.com/watch?v=NdIyXxFH7s0) How to Determine A+ Liquidity? Asia Range Model · Manipulation Series (Ep.13) | [01:06](https://www.youtube.com/watch?v=NdIyXxFH7s0&t=66s) | CISD sonrası fiyatın Asya range ucuna taşınmasını hedefliyor. | "Asya range'in hayına taşımak isteriz" |
| [NdIyXxFH7s0](https://www.youtube.com/watch?v=NdIyXxFH7s0) How to Determine A+ Liquidity? Asia Range Model · Manipulation Series (Ep.13) | [03:54](https://www.youtube.com/watch?v=NdIyXxFH7s0&t=234s) | Short örneğinde hedef Asya low. | "Buradaki Asya Lov'a kadar taşımamız gerekiyor" |
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [09:24](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=564s) | Hedefin önceki likidite seviyeleri olması gerektiğini söylüyor. | "Yani biz Entry aldığımız zaman hedeflerimiz burası olmalı" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [05:16](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=316s) | Hedef: 09:30 öncesi orijinal konsolidasyon yapısı. | "Original consolidation yapısına getireceğim" |
| [QMr3DGh8ZyY](https://www.youtube.com/watch?v=QMr3DGh8ZyY) Scalp tradelemek için sadece bir modele ihtiyaç duysaydım.. | [11:49](https://www.youtube.com/watch?v=QMr3DGh8ZyY&t=709s) | Hedefin A+ draw (Asya range ucu) olduğunu söylüyor. | "fiyatı nereye sürebiliriz? A plus draw'a sürebiliriz" |

## R14

**A+ seviyeleri.** Asya range (20:00–00:00 NY) ve önceki gün high/low.

**Kodda:** Seçicilik turu F1/F2: Asya H/L ve önceki gün H/L.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [QMr3DGh8ZyY](https://www.youtube.com/watch?v=QMr3DGh8ZyY) Scalp tradelemek için sadece bir modele ihtiyaç duysaydım.. | [07:23](https://www.youtube.com/watch?v=QMr3DGh8ZyY&t=443s) | Asya range'i 20:00-00:00 (NY) olarak tanımlıyor. | "Burada Asya Range'i hangi saatler arasında? 20.00 ve 00.00 arasında mevcut" |
| [O_H13qPRyI4](https://www.youtube.com/watch?v=O_H13qPRyI4) Endeks Tradelemek için İhtiyacınız Olan Her Şey - 9.30 Manipulation - 1st Presented FVG - Macro' | [04:47](https://www.youtube.com/watch?v=O_H13qPRyI4&t=287s) | A+ draw'ı Asya high/low ve önceki gün high/low olarak tanımlıyor. | "Asya haylı, Asya lovu, önceki günün hayı, lovu gibi spesifik seviyeler" |
| [NdIyXxFH7s0](https://www.youtube.com/watch?v=NdIyXxFH7s0) How to Determine A+ Liquidity? Asia Range Model · Manipulation Series (Ep.13) | [05:33](https://www.youtube.com/watch?v=NdIyXxFH7s0&t=333s) | Telegram'a attığı işlemin hedefinin Asya range low (A+ draw) olduğunu söylüyor. | "NQ as range low hedefli a + draw" |
| [NPKjTTcsEME](https://www.youtube.com/watch?v=NPKjTTcsEME) Range Manipülasyonu Nasıl Kullanılır? · Manipulation Series (Ep.4) | bulunamadı | bulunamadı: bu videoda Asya penceresi 19:00-00:00 (Gemini notu); transkriptte saat aralığı doğrulanmadı. |  |

## R15

**Asya konsolide / hedefe yakınsa işlem yok.** Asya range'i konsolide olmalı; 09:30'da fiyat hedefe çok yakınsa işlem alınmaz.

**Kodda:** Seçicilik turu F3 (Asya range'i/ATR geçmiş medyanın altında) ve F2 (hedef hâlâ açık).

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [QMr3DGh8ZyY](https://www.youtube.com/watch?v=QMr3DGh8ZyY) Scalp tradelemek için sadece bir modele ihtiyaç duysaydım.. | [08:51](https://www.youtube.com/watch?v=QMr3DGh8ZyY&t=531s) | Asya range'inin konsolide olması gerektiğini söylüyor. | "Asya Range'imiz kesinlikle bir consolidation durumunda olmalı" |
| [QMr3DGh8ZyY](https://www.youtube.com/watch?v=QMr3DGh8ZyY) Scalp tradelemek için sadece bir modele ihtiyaç duysaydım.. | [08:16](https://www.youtube.com/watch?v=QMr3DGh8ZyY&t=496s) | Büyük Asya hareketi yerine konsolide Asya range'i istiyor. | "Bizim için önemli olan konsolide durumunda bir Asya Range'dir" |
| [QMr3DGh8ZyY](https://www.youtube.com/watch?v=QMr3DGh8ZyY) Scalp tradelemek için sadece bir modele ihtiyaç duysaydım.. | [14:11](https://www.youtube.com/watch?v=QMr3DGh8ZyY&t=851s) | 09:30'da fiyat Asya range hedefine çok yakınsa genelde işlem almadığını söylüyor. | "Asya Range'e çok yakınsak ben genelde trade almamaya çalışıyorum" |
| [NdIyXxFH7s0](https://www.youtube.com/watch?v=NdIyXxFH7s0) How to Determine A+ Liquidity? Asia Range Model · Manipulation Series (Ep.13) | [00:33](https://www.youtube.com/watch?v=NdIyXxFH7s0&t=33s) | Aynı konsolide Asya koşulunu tekrarlıyor (Asya Range Modeli). | "Burada net bir konsolidasyon yapısında bir AS rangei görmek isteriz" |

## R16

**İşlem sıklığı.** Her gün kurulum yok; ayda 4–5 / haftada 2–3 kurulum.

**Kodda:** Test edilen kurallar neredeyse her gün tetikleniyor (bkz. README §4a).

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [20:46](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=1246s) | Haftada en fazla 3-4 gün işlem aldığını söylüyor. | "haftada da genelde maksimum 3 veya 4 gün trade atarak geçiriyorum" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [21:08](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=1268s) | Piyasa kurulum sunmazsa işlem almadığını söylüyor. | "sunmazsa hiçbir işlem almam" |
| [P90uzJlCF-Q](https://www.youtube.com/watch?v=P90uzJlCF-Q) Model #2 - Find the Direction of the Day at 9:30 · Pattern Recognition Series (Ep.15) | [15:32](https://www.youtube.com/watch?v=P90uzJlCF-Q&t=932s) | Endekste her gün işlem yapmanın zarar verdiğini, bu tür akışların sık gelmediğini söylüyor. | "her gün trade etmenin insanı belli bir yerden sonra zarar verdiğinin göstergesidir" |
| [agFOlpMucxA](https://www.youtube.com/watch?v=agFOlpMucxA) Range Manipülasyonu: Asıl Hareketi Yakalamak · Pattern Recognition Series (Ep.23) | [05:41](https://www.youtube.com/watch?v=agFOlpMucxA&t=341s) | FPFVG tarzı modelin her gün gerçekleşmediğini, ayda dört-beş giriş sunduğunu söylüyor. _(öncelikli listede olmayan video (Pattern Recognition Ep.23))_ | "ayda size dört tane, beş tane" |
| [mwqtK5eAgtE](https://www.youtube.com/watch?v=mwqtK5eAgtE) Manipülasyon Stratejisi ile aldığım işlem.. (+$2000) · Manipulation Series (Ep.14) | [17:37](https://www.youtube.com/watch?v=mwqtK5eAgtE&t=1057s) | Haftada 2-3 (altyazıda '23') benzer kurulumun yeterli olduğunu söylüyor. _(öncelikli listede olmayan video (Manipulation Ep.14))_ | "Aslında haftada 23 tane Bu şekildeki setup çokça yeterli olur" |
| [P10jGXT6xck](https://www.youtube.com/watch?v=P10jGXT6xck) One Shot One Kill: The Only Pattern You Need · Pattern Recognition Series (Ep. 20) | [18:34](https://www.youtube.com/watch?v=P10jGXT6xck&t=1114s) | Kondisyon filtresiyle ayda yaklaşık beş işlem alınacağını söylüyor. _(öncelikli listede olmayan video (Pattern Recognition Ep.20), hipotetik örnek)_ | "ayda eee beş tane işlem alacaksınız" |
| [bodxOMvKgas](https://www.youtube.com/watch?v=bodxOMvKgas) Fon Hesaplarıyla Para Kazanmak İçin İhtiyacınız Olan Her Şey | [21:31](https://www.youtube.com/watch?v=bodxOMvKgas&t=1291s) | Fon hesaplarında haftada iki işlemin yeterli olduğunu söylüyor. _(öncelikli listede olmayan video; fon hesapları bağlamı)_ | "haftada iki işlem bence optimal bir işlem seviyesi" |

## R17

**Serinin kapsamı (iddia ve sınırları).** Seri, sıfırdan başlayan biri için herkese açık bir eser; bazı modeller ve koşullar videolarda yok.

**Kodda:** Test edilen iddia (README §1); private modeller test kapsamı dışında (README §5).

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [9TER4TqLcoY](https://www.youtube.com/watch?v=9TER4TqLcoY) Philosophy of Becoming a Trader from Zero - DREYKO '25 Series Ep.1 | [06:05](https://www.youtube.com/watch?v=9TER4TqLcoY&t=365s) | Manipülasyon serisini 'arkamda bir eser bırakmak' amacıyla çektiğini söylüyor. | "Arkamda bir eser bırakmaktı" |
| [9TER4TqLcoY](https://www.youtube.com/watch?v=9TER4TqLcoY) Philosophy of Becoming a Trader from Zero - DREYKO '25 Series Ep.1 | [06:30](https://www.youtube.com/watch?v=9TER4TqLcoY&t=390s) | Tamamlayıcı serinin sıfırdan başlayan biri için olduğunu söylüyor. | "Sıfırdan başlayan bir insan için" |
| [9TER4TqLcoY](https://www.youtube.com/watch?v=9TER4TqLcoY) Philosophy of Becoming a Trader from Zero - DREYKO '25 Series Ep.1 | [06:41](https://www.youtube.com/watch?v=9TER4TqLcoY&t=401s) | Yaklaşık 60-70 videoluk iki serinin bir yıllık çalışma eseri olacağını söylüyor. | "bir insanın bir yıl boyunca uzun soluklu bir çalışabileceği bir eser olacak" |
| [9TER4TqLcoY](https://www.youtube.com/watch?v=9TER4TqLcoY) Philosophy of Becoming a Trader from Zero - DREYKO '25 Series Ep.1 | [06:48](https://www.youtube.com/watch?v=9TER4TqLcoY&t=408s) | Serinin tamamının YouTube'da herkese açık olacağını söylüyor. | "tamamen YouTube'da public bir şekilde olacak bu videolar" |
| [9TER4TqLcoY](https://www.youtube.com/watch?v=9TER4TqLcoY) Philosophy of Becoming a Trader from Zero - DREYKO '25 Series Ep.1 | [08:49](https://www.youtube.com/watch?v=9TER4TqLcoY&t=529s) | Bazı modellerini ve notlarını Telegram grubunda (Dreyko's Cave) paylaştığını söylüyor. _(kapsam beyanı)_ | "bazı modellerim tamamen burada Dreos Cave'de paylaşıyorum" |
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [14:17](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=857s) | Bu videoda tüm koşulları anlatmadığını söylüyor; örnek olarak 5 dk FVG girişinden bahsetmediğini belirtiyor. _(kapsam beyanı)_ | "Çünkü ben burada tüm kondisyonlardan bahsetmiyorum" |
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [14:12](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=852s) | İzleyiciden örnek günü kendisi işliyormuş gibi çalışmasını istiyor; yalnızca videoyu izlemenin yeterli olmadığını söylüyor. _(kapsam beyanı)_ | "sadece videoyu izlemek bile eee, yeterli değil" |
| [NdIyXxFH7s0](https://www.youtube.com/watch?v=NdIyXxFH7s0) How to Determine A+ Liquidity? Asia Range Model · Manipulation Series (Ep.13) | [00:19](https://www.youtube.com/watch?v=NdIyXxFH7s0&t=19s) | Asya range modelinin private eğitime özgü olduğunu söylüyor. _(kapsam beyanı)_ | "tamamen private olarak hazırladığım eğitime özgü" |
| [KDsDDr3FSP4](https://www.youtube.com/watch?v=KDsDDr3FSP4) ICT Macro' Nasıl Tradelenir? DREYKO ile LiveTrading · Manipulation Series (Ep.15) | [24:08](https://www.youtube.com/watch?v=KDsDDr3FSP4&t=1448s) | News modelini private kursta anlattığını söylüyor. _(kapsam beyanı)_ | "buradaki news model da zaten private kursa anlatıyorum" |
| [QMr3DGh8ZyY](https://www.youtube.com/watch?v=QMr3DGh8ZyY) Scalp tradelemek için sadece bir modele ihtiyaç duysaydım.. | [03:37](https://www.youtube.com/watch?v=QMr3DGh8ZyY&t=217s) | Neden tamamen otomatikleştirmediği sorusuna stratejiyi kendine sakladığını söyleyerek cevap veriyor. _(kapsam beyanı)_ | "Buradaki stratejiyi aslında tamamen kendime saklıyorum" |
| [P90uzJlCF-Q](https://www.youtube.com/watch?v=P90uzJlCF-Q) Model #2 - Find the Direction of the Day at 9:30 · Pattern Recognition Series (Ep.15) | [10:15](https://www.youtube.com/watch?v=P90uzJlCF-Q&t=615s) | Bazı bilgilerin premium olduğunu söylüyor. _(kapsam beyanı)_ | "Bu biraz premium bir bilgi" |

## R18

**4 Haziran 2025 canlı işlemi.** FPFVG'ye limit short, hedef opening range gap'in 0.5'i.

**Kodda:** Kod aynı günü FPFVG short olarak yakalıyor (README §3).

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [KDsDDr3FSP4](https://www.youtube.com/watch?v=KDsDDr3FSP4) ICT Macro' Nasıl Tradelenir? DREYKO ile LiveTrading · Manipulation Series (Ep.15) | [07:40](https://www.youtube.com/watch?v=KDsDDr3FSP4&t=460s) | Limit satış emri koyuyor (FPFVG'ye). | "Şöyle limit sat" |
| [KDsDDr3FSP4](https://www.youtube.com/watch?v=KDsDDr3FSP4) ICT Macro' Nasıl Tradelenir? DREYKO ile LiveTrading · Manipulation Series (Ep.15) | [08:25](https://www.youtube.com/watch?v=KDsDDr3FSP4&t=505s) | Oluşan 1dk FPFVG'yi işaret ediyor. | "Burası artık first presented feile gapimiz" |
| [KDsDDr3FSP4](https://www.youtube.com/watch?v=KDsDDr3FSP4) ICT Macro' Nasıl Tradelenir? DREYKO ile LiveTrading · Manipulation Series (Ep.15) | [08:38](https://www.youtube.com/watch?v=KDsDDr3FSP4&t=518s) | İşleme girdiğini söylüyor (order block + SMT + FPFVG birlikte). | "şu an işleme girdik" |
| [KDsDDr3FSP4](https://www.youtube.com/watch?v=KDsDDr3FSP4) ICT Macro' Nasıl Tradelenir? DREYKO ile LiveTrading · Manipulation Series (Ep.15) | [15:59](https://www.youtube.com/watch?v=KDsDDr3FSP4&t=959s) | FPFVG'ye dokunulunca yeniden giriş yaptığını söylüyor. | "first present fa'ten yeniden aldım" |
| [KDsDDr3FSP4](https://www.youtube.com/watch?v=KDsDDr3FSP4) ICT Macro' Nasıl Tradelenir? DREYKO ile LiveTrading · Manipulation Series (Ep.15) | [24:36](https://www.youtube.com/watch?v=KDsDDr3FSP4&t=1476s) | Hedefin opening range gap'in 0.5 seviyesi olduğunu ve tam o seviyeye iğne atıldığını söylüyor. | "milimetrik 0.5 seviyesi" |
| [KDsDDr3FSP4](https://www.youtube.com/watch?v=KDsDDr3FSP4) ICT Macro' Nasıl Tradelenir? DREYKO ile LiveTrading · Manipulation Series (Ep.15) | bulunamadı | Tarih '4 Haziran 2025' ve ES enstrümanı transkriptte geçmiyor; yalnızca Gemini (video görüntüsü). |  |

## R19

**"Kendiniz backtest edin".** İzleyiciden günleri kendisinin incelemesini, veri tutmasını istiyor.

**Kodda:** Bu repo tam olarak bunu yapıyor.

| Video | Dakika | Ne söyleniyor | Altyazıdan alıntı |
|---|---|---|---|
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [13:53](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=833s) | İzleyiciye 15 Temmuz gününü kendi başına, 07:00'den itibaren inceleyip backtest etmesini söylüyor. | "itibaren bir inceleyin backtest'le" |
| [BvGdVyo4UY0](https://www.youtube.com/watch?v=BvGdVyo4UY0) Günün İlk Girişini Kaçırma: 1st Presented FVG · Pattern Recognition Series (Ep.16) | [14:03](https://www.youtube.com/watch?v=BvGdVyo4UY0&t=843s) | 09:30'da sanki kendisi işlem alıyormuş gibi çalışmasını istiyor. | "sanki kendiniz trade'liyormuş gibi, lütfen trade'leyin" |
| [O_H13qPRyI4](https://www.youtube.com/watch?v=O_H13qPRyI4) Endeks Tradelemek için İhtiyacınız Olan Her Şey - 9.30 Manipulation - 1st Presented FVG - Macro' | [24:41](https://www.youtube.com/watch?v=O_H13qPRyI4&t=1481s) | Sonunda izleyiciye 'data tutun' ve kendi verisiyle denemesini söylüyor (nerede hata yapıyorsunuz, win rate). | "data tutun" |
| [P90uzJlCF-Q](https://www.youtube.com/watch?v=P90uzJlCF-Q) Model #2 - Find the Direction of the Day at 9:30 · Pattern Recognition Series (Ep.15) | [16:32](https://www.youtube.com/watch?v=P90uzJlCF-Q&t=992s) | ES tarafını izleyicinin kendisinin analiz etmesini öneriyor. | "ES tarafını da kendiniz analizleyebilirsiniz" |
| [1mi2eQ5YoCc](https://www.youtube.com/watch?v=1mi2eQ5YoCc) ICT Macro Nedir? - Algoritmik Fiyat Hareketi · Manipulation Series (Ep.12) | [19:45](https://www.youtube.com/watch?v=1mi2eQ5YoCc&t=1185s) | İzleyiciden 09:50 makrosunu canlı testlemesini istiyor. | "Makroları özellikle 950'un makrosunu live testlemeye çalışın" |
