# Dreyko: kodlanabilir model taslağı (proje sırasında yazıldı; sonuç NO-GO, backtest sonradan kullanıcı kararıyla yapıldı: `backtest/bt_rapor.md`)

**Kaynaklar:** (Bu belge proje sırasında yazıldı; aşağıdaki "Durum" satırı sonradan güncellendi. Sonuç: NO-GO, bkz. README.)
- YZ destekli transkript taraması, 67/68 video: transkript tarama notları (telif nedeniyle yayınlanmadı).
- Gemini Argon video analizleri: `kaynaklar/gemini_notlari.md`. Toplam 10 video: XeXiuJEYIiU, P90uzJlCF-Q, O_H13qPRyI4, NdIyXxFH7s0, ogHB0f9b6Fk, 1mi2eQ5YoCc, QMr3DGh8ZyY, KDsDDr3FSP4, NPKjTTcsEME, BvGdVyo4UY0. (mLCStLwgIJo iki kez boş döndü, atlandı.)

**Gemini'den gelen netleştirmeler (7 Kasım):**
- **Asia Range (H3):** Asya kutusu 20:00–00:00 NY. 09:30'da Asya'nın bir ucu süpürülür. Sweep bacağındaki son 3dk FVG body ile ters kırılınca IFVG olur. Sonraki mum IFVG'nin EQ'suna değip saygı gösterirse market emir. Stop sweep ucunda, TP Asya'nın karşı ucunda. İşlem genelde 09:50–10:10 ve 10:50–11:10 makroları içinde. Asya seansı "konsolide" değilse o gün atlanıyor; 09:30'da fiyat hedefe çok yakınsa da atlanıyor. İki filtre için de eşiği biz tanımlayacağız.
- **CISD tanımı:** Sweep/TS dibini yaratan ardışık karşı yönlü mumların (örnekte 3) ilkinin açılışının ötesinde body kapanışı. "Rahatlama rallisi" tuzağı: 09:30'daki ilk tepki mumunda ya da ilk IFVG'de girilmez. Fiyatın ikinci kez uca sarkması (Turtle Soup) ve CISD beklenir.
- **TP1 = FPFVG:** 1mi2'de FPFVG ilk kâr hedefi olarak kullanılıyor.
- **News Model:** Mekanik olarak çekirdek modelin CPI/NFP günü versiyonu. Ayrı bir hipotez değil, alt küme/filtre olarak test edilmesi daha uygun.
- **Lunch makrosu:** 11:30–13:00 (A+ indikatörü).

**İkinci tur netleştirmeler (7 Kasım öğle):**
- **FPFVG (BvGd, en net kaynak):** 09:30'dan sonraki ilk 1dk FVG (örnekte 09:31–09:33 üçlüsü). Asıl giriş 09:50–10:10 makrosundaki FPFVG retesti; alternatif olarak makroda fiyatı FPFVG'ye taşıyan 1dk FVG'nin 10:10 sonrası IFVG'ye dönmesi. "Yüksek olasılıklı işlemler 10:50–11:10 ile biter" → FPFVG geçerliliği için doğal üst sınır ~11:10.
- **Giriş emri:** KDsD canlı işleminde FPFVG EQ'sunun hemen üstüne **limit** emir (09:43, makrodan önce). BvGd'de FPFVG kenarı/ortası. Yani hem EQ-limit hem kenar-limit Dreyko'nun pratiğinde var.
- **Stop:** Dar stop (FPFVG ötesi) önerilmiyor; bir üstteki yapısal tepe / 5dk FVG ötesi. KDsD'de sweep tepesi + birkaç tick.
- **Hedef adayları:** Önceki günlerin saatlik dip/tepeleri (sell/buy-side likidite), **NY Opening Range Gap'in 0.5'i** (önceki seans kapanışı–09:30 açılış boşluğu, KDsD), 08:30 haber mumunun karşı ucu.
- **Risk:** Günde en fazla 2 stop, sonra gün kapanır (BvGd). Backtest'e platform kuralı olarak eklenebilir (METODOLOJI.md §6).
- **SMT çıkış kuralı (NPKj):** Long'dayken NQ referans tepeyi alıp ES alamazsa çık (ve tersi). SMT burada giriş filtresinden çok çıkış sinyali.
- **Asya penceresi tutarsız:** NPKj'de 19:00–00:00 (bir örnekte 19:00–01:00), A+ indikatöründe 20:00–00:00. İki değer de deneme sayacına girer.
- **Endekste iğne yanıltır, body kapanışı esas** (NPKj): seviye kırılımları/FVG teyitleri body kapanışıyla tanımlanacak.
- **OOS uyarısı:** BvGd ve QMr3'teki örnek günler 2026'dan (OOS). Yalnızca kural tanımı için okundu; fiyatlara/sonuçlara bakılmadı ve kural seçiminde örnek günün sonucu kullanılmayacak.

**Durum:** Adım 0 (`adim0/adim0_rapor.md`) ve Dreyko'nun kendi seçicilik kurallarıyla ön kayıtlı ikinci tur (`adim0/secicilik_rapor.md`): kodlanan tetiklerin hiçbiri bilgi taşımıyor, ön kayda göre NO-GO. Bu belge bir hipotez adayıdır, bulgu değildir. Kullanıcı kararları aşağıda kayıtlı. Adım 0 (olay çalışması) sonuçları kullanıcıya raporlanmadan ve kullanıcı onay vermeden hiçbir backtest çalıştırılmaz (METODOLOJI.md §3).

## Çekirdek fikir (videolar arasında tutarlı)
NQ için, ES'yi SMT teyidi olarak kullanarak, New York saatiyle. Dreyko yalnızca 09:30'dan sonra işlem alıyor ve günde 1–2 işlemle sınırlı kalıyor.
1. **Ön koşul: 09:30 öncesi likidite.** "Her gün manipülasyon aranmaz." İki koşuldan biri gerekir:
   - (a) Açılış öncesinde alınmamış likidite var: equal high/low, LRLR (kademeli dipler veya tepeler), paralel kanal ya da 08:00 mumunun ucu.
   - (b) Fiyat A+ draw'a gitmeden önce bir key level'a dokunmuş.

   **A+ draw:** Asya range'inin high/low'u (20:00–00:00 NY) ve önceki günün high/low'u.
2. **09:30 manipülasyonu:** Bu likiditenin bir tarafı süpürülür (sweep).
3. **SMT:** Sweep sırasında NQ ve ES'den biri yeni uç yapar, diğeri yapmaz. Dreyko SMT'yi tek başına sinyal olarak kullanmıyor, "emniyet kemeri" olarak kullanıyor.
4. **Üç şart:** HTF key level + SMT + manipülasyon. "Fazlası sisteme zarar verir."
5. **First Presented FVG (FPFVG):** 09:30'dan sonra oluşan ilk 1dk FVG. 09:30 mumunun kendi FVG'si sayılmaz. FPFVG günün "gerçek S/R"si kabul ediliyor: fiyat üstünde kalırsa buyside'a, altında kalırsa sellside'a gider. Body ile kırılırsa IFVG olur ve ters yönde çalışır. FPFVG yoksa işlem yok.
6. **Giriş türleri:**
   - CSD: ardışık momentumsuz mumların body ile aşılması; kapanışta market emir.
   - IFVG flip sonrası retest.
   - FPFVG'nin EQ'suna (0.5) geri çekilme.

   Uyarı: 09:30'dan sonraki ilk 5 dk'daki karşı yönlü "rahatlama" mumuna erken atlanmaz.
7. **Stop:** Manipülasyon (sweep) ucunun ötesi. Videolarda sayısal bir mesafe verilmiyor; Dreyko "geniş stop" diyor.
8. **Hedef ve çıkış:**
   - TP1: 09:30 öncesi range'in karşı ucu. Pozisyonun %70–80'i burada kapatılır.
   - TP2: HTF likidite (A+ draw, PDH/PDL).
   - Range EQ'sunda kâr alınır.
   - Karşı endeks hedefi almıyorsa pozisyondan çıkılır.
9. **Zaman:**
   - Expansion'ı 09:50–10:10 makrosu taşır. Diğer pencereler 10:50–11:10 ve 11:50–12:10.
   - Pratikte Dreyko 09:30–11:00 arasına bakıyor.

## Kodlamaya aday hipotezler (tarafsız, iki yönlü)
| Kod | Varyant | Tetik | Giriş | Stop | Hedef |
|---|---|---|---|---|---|
| H1 | FPFVG yön/S-R | 09:30 sonrası ilk 1dk FVG | FPFVG EQ retesti (devam) **veya** FPFVG body ile kırılınca ters yön (IFVG) | FPFVG'yi yaratan bacağın ucu | Sabit R (2R/3R) veya karşı likidite; zaman çıkışı 11:10 |
| H2 | Model #1 sweep-reversal | 09:30–10:00 arası pre-market range (08:00–09:30) ucunun süpürülmesi | Sweep bacağındaki FVG IFVG olunca kapanışta market | Sweep ucu ötesi | TP1 range'in karşı ucu, TP2 A+ draw/PDH-PDL |
| H2b | Sweep + TS + CISD (1mi2) | H2 tetiği + ilk tepkiden sonra ikinci kez uca sarkma (TS) | N ardışık karşı yönlü mumun ilkinin açılışı ötesinde body kapanışı (CISD) | TS ucu ötesi | TP1 FPFVG, TP2 range'in karşı ucu |
| H2+SMT | H2 + ES/NQ SMT filtresi | H2 tetiği + sweep sırasında ES/NQ uyumsuzluğu | (H2 ile aynı) | (H2 ile aynı) | (H2 ile aynı) |
| H3 | Asia Range Model | 09:30'da 09:30 öncesi range ucu süpürülür, Asya range'inin karşı ucu hedeftir | 3dk IFVG | Sweep ucu ötesi | Asya range'inin karşı ucu |
| H5 | Lunch Range "1-4" (NPKj) | 12:00–13:00 range'inin bir ucu 13:00–13:30'da süpürülür | Range içine body kapanışla dönüş | Sweep ucu ötesi | Range'in karşı ucu / önceki gün H-L; zaman çıkışı 16:00 |
| H4 | Makro filtresi | H1/H2 + girişin 09:50–10:10 içinde olması | (H1/H2 ile aynı) | (H1/H2 ile aynı) | (H1/H2 ile aynı) |
| H0 | Negatif kontrol | Aynı saatlerde koşulsuz / rastgele yön | (H1/H2 ile aynı) | (H1/H2 ile aynı) | (H1/H2 ile aynı) |

Ayrıca test edilebilir yan iddialar (daha sonra):
- News Model: yalnızca CPI/NFP; yılda yaklaşık 24 gün, istatistik gücü zayıf.
- Range manipülasyonu.
- Judas/PO3: gece yarısı açılışından sapma.
- D1-D2-D3 mum kuralı.
- "Sol taraf ne kadar yavaşsa sağ taraf o kadar hızlı" (MMXM).

## Kodlanamayan / sübjektif kısımlar
- **HTF bias:** 4sa OB, daily FVG kuadrantı, COT. Görsel ve takdirî. İlk turda bias'sız test edilir.
- **"Key level" tanımı videodan videoya değişiyor:** bazen gün içi LRLR, bazen 4sa FVG. Bu iki versiyon ayrı ayrı ele alınır.
- **TF seçimi:** Dreyko 1/3/5/15dk arasında "en temiz görüneni" seçiyor. Ana TF 1dk alınır; diğerleri ayrı varyant sayılır ve deneme sayacına girer.
- **Piramit ve parçalı çıkış:** İlk turda tek giriş, tek çıkış.

## Kullanıcı kararları (7 Kasım 2026)
Sonuçlar görülmeden alındı. Ayrıntı ve deneme sayacı: `karar_gunlugu.md`.

| # | Konu | Karar |
|---|---|---|
| 1 | FPFVG penceresi | İki varyant: **A** oluşum 09:30–10:00, retest 11:10'a kadar; **B** oluşum 09:30–09:45, retest 10:10'a kadar. Pencerede FVG yoksa o gün işlem yok. |
| 2 | Giriş (H1) | FPFVG'nin **yakın kenarına limit** (retestte fiyatın ilk değdiği kenar: bearish FPFVG'de alt kenar, bullish'te üst kenar). Dolmazsa işlem yok. H2/H2b girişleri tanımlandığı gibi kapanışta sinyal, sonraki bar açılışında market. |
| 3 | Hedef / çıkış | İki varyant: **L** likidite (09:30 öncesi 08:00–09:30 range'inin karşı ucu), **R** sabit 2R. Tutmazsa zaman çıkışı **12:00**. |
| 4 | SMT | Ablation adımı: önce SMT'siz baz, sonra SMT filtresi eklenmiş hali. |
| 5 | Enstrüman | Kurallar **NQ**'da kurulur; **ES**'de hiç ayar yapılmadan çapraz test. |
| 6a | Eksik dakika | FVG yalnızca 3 ardışık dakika barla tanımlanır; boşluklu üçlü atlanır. |
| 6b | Dışlanan günler | Yalnızca RTH'siz günler. Yarım günler kalır. Mart 2020 kalır; sonuç onlu/onsuz ayrıca raporlanır. |
| 7 | Asya penceresi | 20:00–00:00 NY. 19:00–00:00 yalnızca sağlamlık testi. |
| 8 | Kapsam | İlk tur: **H1, H2, H2b, H0** (+SMT ve makro ablation). H3 Asia Range ve H5 Lunch ikinci tura. |
| — | Adım 0 | Backtest'ten önce olay çalışması (aşağıda). Sonuçlar kullanıcıya raporlanır; backtest'e neyin gireceğine kullanıcı karar verir. |

## Adım 0 planı: olay çalışması (backtest yok, yalnızca IS 2020–2025)
- **Olaylar (tetikler):** (i) FPFVG oluşumu (yön = FVG yönü), (ii) FPFVG'nin ilk retesti, (iii) 08:00–09:30 range ucunun 09:30–10:00 arası süpürülmesi, (iv) sweep sonrası IFVG, (v) TS + CISD.
- **Hedef etiket (donduruldu):** Olay barının kapanışından sonraki bar açılışından itibaren +15, +30, +60 dk ve 12:00'ye kadar getiri; önceki tamamlanmış günün ATR(14)'üne bölünür. Her olay için **iki yön tarafsız** (devam vs dönüş) raporlanır.
- **Raporlanacaklar:** Olay sayısı, ortalama/medyan normalize getiri, t-istatistiği, yıl bazında işaret istikrarı, long/short ayrımı, aynı saatte koşulsuz baza göre fark, MFE/MAE dağılımı, SMT var/yok ve makro içi/dışı kırılımları, Bonferroni + BH-FDR (toplam test sayısı kayda geçer).
- Sızıntı birim testleri: karar anı ve sonrası barlar bozulunca tetik ve özniteliklerin değişmediği gösterilir.

## İddia edilen performans
- **İstatistik:** İncelenen videolarda win rate, PF, örneklem büyüklüğü ya da maliyet yok. Sadece seçilmiş tek günler gösteriliyor ve bu örneklerdeki RR değerleri 2.7–5.8.
- **Frekans iddiası tutarsız:** Bir yerde "ayda 4–5 kurulum", başka yerde "haftada 2–3 kurulum" deniyor.
