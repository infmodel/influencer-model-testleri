# Dreyko: karar günlüğü ve deneme sayacı

METODOLOJI.md §7: her karar gerekçesiyle, her varyant sayılarak kaydedilir. DSR ve FDR'deki test sayısı buradan alınır.

## Kararlar

| Tarih | Karar | Gerekçe | Kim |
|---|---|---|---|
| 2026-11-06 | `session_date` yükleyicide `datetime_ny`'den türetilir (>=18:00 → ertesi gün) | Processed dosyada DST-bitiş pazarları yanlış etiketli (6×360 satır); veri dosyasına dokunulmadı | YZ asistanı (Faz 0) |
| 2026-11-06 | 2026 OOS kilitli; Gemini'nin 2026 örnek günleri (QMr3, BvGd) yalnızca kural tanımı için okundu | Kilitli OOS ilkesi | YZ asistanı |
| 2026-11-07 | mLCStLwgIJo (MMXM) Gemini analizi atlandı | Argon iki kez boş cevap; MMXM ilk turda kodlanmıyor | YZ asistanı |
| 2026-11-07 | FPFVG penceresi iki varyant: A (oluşum ≤10:00, retest ≤11:10), B (oluşum ≤09:45, retest ≤10:10) | Videolarda sayısal sınır yok; iki makul okuma | Proje sahibi |
| 2026-11-07 | H1 girişi: FPFVG yakın kenarına limit | Kullanıcı tercihi (BvGd pratiği) | Proje sahibi |
| 2026-11-07 | Hedef iki varyant: L (08:00–09:30 range karşı ucu), R (sabit 2R); zaman çıkışı 12:00 | Dreyko likidite hedefliyor; sabit R mekanik karşılaştırma | Proje sahibi |
| 2026-11-07 | SMT ablation adımı olarak | Filtre katkısı ayrıca gösterilmeli (§3 Aşama 4) | Proje sahibi |
| 2026-11-07 | NQ ana, ES ayarsız çapraz test | §6; Dreyko ağırlıkla NQ | Proje sahibi |
| 2026-11-07 | FVG yalnızca 3 ardışık dakika barla; boşluklu üçlü atlanır | Sahte FVG üretmemek | Proje sahibi |
| 2026-11-07 | Yalnızca RTH'siz günler dışlanır; yarım günler ve Mart 2020 kalır (Mart 2020 onlu/onsuz raporlanır) | Sabah seansı yarım günlerde tam | Proje sahibi |
| 2026-11-07 | Asya 20:00–00:00 NY; 19:00 yalnızca sağlamlık | Dreyko'nun A+ indikatör tanımı | Proje sahibi |
| 2026-11-07 | İlk tur kapsamı H1, H2, H2b, H0 (+SMT, makro ablation); H3, H5 ikinci tur | Deneme sayısını sınırlamak | Proje sahibi |
| 2026-11-07 | Backtest öncesi Adım 0 olay çalışması | METODOLOJI.md §3 Aşama 3 | Proje sahibi |
| 2026-11-07 | Adım 0 ek tanımları (sonuçlardan önce, kodda sabitlendi): PM range 08:00–09:29 (≥60 bar); sweep 09:30–09:59, 09:30 açılışı range içinde olmalı, aynı barda iki uç → olay yok; IFVG için sweep bacağı FVG'si 3. barı ≥09:00; TS = range içine kapanıştan sonra ilk sweep ucunun yeniden aşılması; CISD = uca götüren ardışık karşı mumların ilkinin açılışı (uç barında ya da bir önceki barda biten dizi); IFVG/CISD tetiği ≤11:09; makro = giriş barı 09:50–10:09; SMT = karar anına kadar iki endeksten yalnız birinin PM ucunu alması; ATR(14) önceki seanslardan | Videolardaki tanımların en sade mekanik karşılığı | YZ asistanı |
| 2026-11-07 | Adım 0 sonucu: tüm olaylar/ufuklar/alt kümelerde BH q ≥ 0.84 (NQ min 0.996); etki < ±0.01 ATR; MFE≈MAE; OOF AUC 0.49–0.55. Öneri NO-GO (adim0/adim0_rapor.md) | — | YZ asistanı (karar proje sahibinde) |

## Deneme sayacı (ön-kayıtlı varyantlar, ilk tur)

| Hipotez | Varyant eksenleri | Konfigürasyon sayısı |
|---|---|---|
| H1 FPFVG | pencere A/B × hedef L/R × SMT var/yok × makro var/yok | 16 |
| H2 sweep-reversal | hedef L/R × SMT var/yok × makro var/yok | 8 |
| H2b TS+CISD | hedef L/R × SMT var/yok × makro var/yok | 8 |
| H0 negatif kontrol | H1/H2 ile aynı saat ve çıkış, koşulsuz/rastgele yön | (kontrol, sayılmaz) |
| **Toplam backtest konfigürasyonu** | | **32** (×2 enstrüman çapraz testte ayrıca raporlanır) |

**Adım 0 test sayısı (ölçüldü, 7 Kasım):** NQ: 192 ham + 192 fazla getiri + 64 öznitelik IC = 448 p-değeri, ayrıca 7 ağaç modeli (LOYO). ES: 448 p-değeri. Toplam 896 p-değeri. Olaylar: FPFVG_form A/B, FPFVG_retest A/B, SWEEP, IFVG, TSCISD (7) × alt küme 7 × ufuk 4. Mart 2020 hariç tekrar (sağlamlık, aynı aile tekrarı). Post-hoc SMT+makro kesişimi: test sayılmadı, kanıt sayılmaz.

Sağlamlık testleri (Asya 19:00, Mart 2020 onsuz vb.) bu sayaca ayrı satır olarak eklenecek.

## Seçicilik turu: ön kayıt (7 Kasım 2026, filtreli sonuçlar görülmeden yazıldı)

**Bağlam ve uyarı:** Kullanıcı Adım 0 sonrası "seçicilik turu" seçti. Adım 0'ın filtresiz sonuçları görüldü, bu tur post-hoc risk taşır. Riski azaltmak için filtreler yalnızca Dreyko'nun videolarda söylediği kurallardan alındı, sonuçlara bakılarak seçilmedi. Eşik gerektiren yerde tek, önceden belirlenmiş değer kullanılır. Olaylar, etiketler ve ufuklar Adım 0 ile aynıdır (yeniden tanımlanmadı).

**Seviyeler (hepsi karar anından önce oluşmuş):**
- Asya H/L: seans gününün 20:00–23:59 (önceki takvim akşamı) barları. Kaynak: A+ indikatörü (QMr3, NdIy).
- PDH/PDL: önceki CME seansının (18:00–17:00) high/low'u. Kaynak: "A+ draw = Asya H/L ve önceki gün H/L" (XeXiu, QMr3).
- 4sa/günlük FVG ve haftalık gap key level'ları bu turda kodlanmadı (sübjektif seçim gerektiriyor).

**Filtreler** (bilgi kesimi: giriş barının açılışından önce kapanmış barlar). d = işlem yönü (olayın doğal yönü):
- **F1, key level manipülasyonu** ("3 şart"ın 1. ve 3. şartı; ön koşul b): İşlem yönünün tersindeki A+ seviyelerinden en az biri (long için Asya low veya PDL, short için Asya high veya PDH) 09:30'a kadar alınmamış olmalı ve 09:30 ile giriş arasında alınmış olmalı. "Alınmamış" ölçümü: Asya seviyesi için 00:00'dan, PDH/PDL için seans açılışından (18:00) itibaren.
- **F2, açık A+ draw:** İşlem yönündeki A+ seviyelerinden en az biri (long için Asya high veya PDH) girişe kadar alınmamış olmalı. Kaynak: "hedef A+ draw" ve "09:30'da fiyat hedefe yakınsa işlem yok" (QMr3). Mesafe eşiği yok; yalnızca hedefin hâlâ açık olması aranır.
- **F3, Asya konsolide:** Asya range'i / ATR, önceki günlerin genişleyen penceredeki medyanının altında olmalı (en az 60 gün geçmiş). Kaynak: QMr3. Eşik = medyan, tek değer.
- **SMT:** Adım 0'daki tanım.

**Alt kümeler (6):** F1 · F2 · F3 · F1∧F2 ("A+ kurulum") · F1∧SMT ("3 şart") · F1∧F2∧F3.

**Birincil hipotez (tek aile, 7 test/enstrüman):** F1∧F2 alt kümesinde, 7 olayın 12:00 getirisi (doğal yönde) sıfırdan büyük. BH-FDR q<0.05 ve NQ'da pozitif ortalama, pozitif medyan ve 6 yılın en az 4'ünde aynı işaret gerekir. ES işaret olarak tutarlı olmalı.

**İkincil (keşif):** 6 alt küme × 7 olay × 4 ufuk = 168 test/enstrüman, ayrı BH ailesi.

**Geçme kuralı:** Birincil aile geçmezse seçicilik turu da NO-GO sayılır ve arşivlenir. İkincil ailede yalnızca q<0.05 olan ve NQ ile ES'de aynı işaretli bir hücre, en fazla gölge izleme adayı olur (METODOLOJI.md §7, post-hoc yasağı).

**Deneme sayacı ekleri:** Birincil 7 + ikincil 168 = 175 test/enstrüman, NQ+ES toplam 350.

**Seçicilik turu sonucu (7 Kasım 2026):** Birincil aile geçmedi (NQ min q 0.27, ES min q 0.96). İkincil ailede q<0.05 yok (NQ min q 0.98, ES 0.59). Ölçülen test sayısı: birincil 7 + ikincil 145 (n<5 olan hücreler hariç) = 152/enstrüman, toplam 304. Ön kayda göre **NO-GO**; gölge izleme adayı yok. NQ'da F1∧F2 FPFVG satırları pozitif ama n=17–25, t<2 ve ES'de tekrarlanmıyor (bulgu sayılmaz). Rapor: adim0/secicilik_rapor.md. Arşivleme kararı kullanıcıda.

## Backtest: kullanıcı kararıyla sapma (7 Kasım 2026, sonuçlar görülmeden yazıldı)

**Sapma:** Adım 0 ve seçicilik turu sinyallerin bilgi taşımadığını gösterdi (NO-GO). Metodolojiye göre bu durumda backtest yapılmaz (METODOLOJI.md §3). Kullanıcı açıkça "backtest yap" dedi; bu yüzden ön kayıtlı 32 varyant (deneme sayacı tablosu) çalıştırılıyor. 2026 OOS'a dokunulmuyor.

**Kurallar** (kullanıcı kararları + taslaktaki stop tanımları; olay tanımları Adım 0 ile aynı):
- **H1:** FPFVG retest. Yakın kenara limit. Dolum için fiyatın kenarı **1 tick geçmesi** gerekir (muhafazakâr); dokunuşta dolum ayrıca duyarlılık olarak raporlanır.
  - Stop: FPFVG'yi yaratan bacağın ucu (09:30'dan FPFVG 3. barına kadarki en yüksek high / en düşük low) + 1 tick.
- **H2:** sweep → IFVG, sonraki bar açılışında market. Stop: tetik anındaki sweep ucu + 1 tick.
- **H2b:** sweep → TS → CISD, sonraki bar açılışında market. Stop: TS ucu + 1 tick.
- **Hedef:**
  - L = 08:00–09:30 range'inin işlem yönündeki ucu. Hedef girişin yanlış tarafındaysa işlem yok.
  - R = 2 × risk.
- **Zaman çıkışı:** 12:00 barının açılışı.
- **SL-first:** Aynı barda stop ve hedef görülürse stop. Boşluklu açılış stopun ötesindeyse açılıştan çıkış. Hedefin ötesinde açılırsa hedef fiyatından çıkış (iyimser değil). Limit dolum barında yalnızca stop kontrol edilir (hedef sayılmaz).
- **Filtreler (ablation):** SMT var/yok × makro (giriş barı 09:50–10:09) var/yok.
- **Maliyet** (veri notları):
  - NQ: $4 RT + taraf başına 1 tick = 0.70 puan.
  - ES: $4 RT + taraf başına 0.5 tick = 0.33 puan.
  - Ratio-adjusted seride puan maliyeti adj_factor ile ölçeklenir.
- **Boyut:** 1 kontrat; sonuçlar hem R hem $ cinsinden.
- **Değerlendirme:**
  - Tekil kârlılık üçlüsü: ortalama>0, medyan>0, NoTop2>0.
  - Yıl tutarlılığı, long/short, PF, max DD.
  - Başabaş maliyet.
  - Rastgele yön permütasyonu: aynı giriş, aynı stop/hedef mesafeleri, 10.000 simülasyon.
  - BH-FDR (32 varyant).
- **NQ'da kural kurulur, ES'de aynen çalıştırılır.**
- **GO şartı:** NQ'da tekil kârlılık üçlüsü + permütasyon q<0.05 + ≥4/6 kârlı yıl + ES'de net pozitif. Bu sağlanmazsa NO-GO.

**Backtest sonucu (7 Kasım 2026):** NQ'da 32 varyantın hiçbiri GO şartını sağlamadı (min perm q 0.72; filtresiz kuralların hepsi maliyet sonrası zararda). ES'de H1+SMT+makro hücreleri pozitif (q min 0.061, n 23–47) ama NQ'da aynı filtre negatif; bulgu sayılmaz. **NO-GO.** Rapor: backtest/bt_rapor.md. Deneme: 64 varyant + 4 duyarlılık.

## Arşiv (7 Kasım 2026)

**Karar:** NO-GO. Model canlıya ya da demoya alınmaz; 2026 OOS hakkı harcanmadı.

**Gerekçe:**
- Olay çalışması, seçicilik turu ve backtest'in üçü de bilgi/avantaj bulamadı.
- Filtresiz kurallar maliyet sonrası zararda.

**Kapsam:**
- Test edilen, videolarda açıkça anlatılan kuralların mekanik okumasıdır.
- Görsel HTF key level katmanı, takdirî çıkışlar ve Dreyko'nun private eğitime ayırdığını söylediği modeller (Asia Range, News) test edilmedi.
- Dreyko'nun kişisel hesap performansı hakkında veri yoktur.

**İddiayla ilişkisi:**
- Dreyko 60–70 videoluk iki seriyi sıfırdan başlayan biri için bir yıl çalışılabilecek, tamamen herkese açık bir eser olarak sunuyor (9TER4TqLcoY, 06:05–06:50).
- Aynı zamanda bazı videolarda tüm koşulları anlatmadığını ve yalnızca izlemenin yeterli olmadığını söylüyor (KURAL_KAYNAKLARI.md, R17).
- Videolarda açıkça öğretilen kurallarla avantaj elde edilemedi. Videolarda öğretilmeyen bir katmanın sonucu değiştirdiği söyleniyorsa, o katmanın yazılı ve test edilebilir tanımı gerekir; incelenen videolarda win rate, örneklem ya da maliyet gösterilmiyor.
