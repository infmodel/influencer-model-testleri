# Adım 0 raporu: Monarus modelleri (MA–MF), olay çalışması

Tarih: 2026-11-08 · Ön kayıt: `on_kayit.md` (sonuçlardan önce) · Kod: `common.py`, `m_ma.py`, `m_me.py`, `m_mf.py`, `m_mb.py`, `m_md.py`, `m_mc.py`, `run_adim0.py` · Testler: `test_monarus_adim0.py` (23/23) · Ham çıktılar: `out/` (`stats.csv`, `ma_stats.csv`, `mc_h0.csv`, `mda*.csv`, `events_*.parquet`, `meta.json`)

**Kapsam:**
- Yalnız IS, 2020–2025. 2026'ya dokunulmadı.
- Enstrümanlar: 6 spot FX (EUR, GBP, CAD, CHF, AUD, JPY), XAUUSD (GC), NQ (yalnız MC).
- Ana gün sınırı NY 17:00, sağlamlık testi TR 00:00.
- Bu bir backtest değil: tek tek olayların SL-first sonucu ölçüldü. Pozisyon boyutu, portföy ve eşzamanlılık kısıtı yok.
- Maliyet data/CLAUDE.md'den alındı. AUD ve JPY spot için geçici değer 1,3 pip.

## Sonuç: Hiçbir model ve varyant Adım 0'ı geçmedi. Videolarda öğretilen kurallar, kodlandıkları haliyle, bu veride kârlı değil.

- **Aday ölçütü:** maliyet sonrası ort. R > 0 ve q < 0,05, ayna farkı q < 0,05, en az 4/6 yıl aynı işaret.
  - 748 işlem anahtarında bu ölçütü geçen yok.
  - Maliyet sonrası pozitif ortalama ve düzeltmesiz p < 0,05 birlikte olan tek anahtar bile yok.
  - Havuzda toplam 2.233 test BH-FDR ile düzeltildi.
- **MA, Monarus'un sayıları gerçekten çıkıyor:** Bias hedefine değme oranı %64–68, iddia %61–80.
  - Ama bu isabet bias'tan değil geometriden geliyor. Flow günü zaten hedefin yakınında kapanıyor; aynı mesafede ters yöndeki seviyeye değme oranı en az onun kadar yüksek.
  - Bias yönünde gün sonu getirisi her enstrümanda sıfır.
- **İşlem modellerinde isabet oranları iddiaların çok altında:**
  - Kazanç oranı her yerde kendi RR'sinin başabaş oranına eşit ya da altında.
  - Ters yönlü ayna işlemden ayırt edilemiyor.
  - Maliyetle hepsi negatif.
- **Negatif kontroller:** Bias filtreleri hiçbir şey eklemiyor:
  - Haftalık bias'lı MF-1 ≈ bias'sız MF-n.
  - Günlük bias'lı ME-1 ≈ bias'sız ME-1n.
- **Öneri:** Hiçbir sinyal backtest'e girmesin. Karar kullanıcının.

## 1. MA: günlük bias isabeti (iddia I-MA2)
Gün sınırı NY17, bias'lı günler (flow + CRT). TR 00:00 sonuçları ±0,01 içinde aynı.

| | n | **Bias hedefine değme** | Monarus iddiası | Karşı uca değme | **Ayna seviyesine değme** (post-hoc) | Bias yönünde getiri (ATR) |
|---|---|---|---|---|---|---|
| EURUSD | 1.254 | **%66,3** | %71,9 | %29,3 | %70,9 | −0,006 |
| GBPUSD | 1.249 | **%66,1** | %66,9 | %29,2 | %69,2 | +0,003 |
| AUDUSD | 1.261 | **%67,7** | %66,8 | %28,5 | %74,0 | −0,027 |
| USDCAD | 1.282 | **%68,3** | %80,1 | %30,0 | %70,1 | −0,032 |
| USDCHF | 1.260 | **%67,9** | %68,3 | %27,5 | %71,3 | +0,006 |
| USDJPY | 1.222 | **%64,8** | — | %27,2 | %67,7 | +0,014 |
| XAUUSD | 1.202 | **%68,0** | %60,7 | %27,4 | %68,8 | +0,009 |

- **Ön kayıtlı testler hepsi "anlamlı" çıktı:** Bias hedefi, karşı uca göre +37–41 puan, koşulsuz baza göre +18 puan daha sık alınıyor (q < 0,001, 6/6 yıl). Flow alt kümesinde oran %70–73, CRT'de %55–64. Monarus'un tablosundaki rakamlar bu veride de çıkıyor.
- **Ama bu kıyaslar adil değil.** Hedefin kapanışa medyan uzaklığı yalnız 0,2 ATR, karşı uç ise genelde ~1 ATR uzakta. Flow günü tanımı gereği ucuna yakın kapanır; yakın seviyeye ertesi gün değmek kolaydır.
- **Ayna kontrolü (post-hoc, sonuç görüldükten sonra eklendi, test sayısına dahil):** Kapanıştan hedef mesafesi kadar **ters yönde** bir seviye alındı. Bu seviyeye değme oranı, bias hedefine değme oranına eşit ya da daha yüksek (fark −0,8 ile −6,3 puan arası, yalnız AUDUSD q = 0,007).
  - Yani bias yön bilgisi taşımıyor. "%67 isabet", herhangi bir yöne 0,2 ATR'lik hareketin olasılığı.
- **Bias yönünde kapanıştan kapanışa getiri:** Koşulsuz ortalamaya göre fark −0,03 ile +0,01 ATR arası. Hiçbiri anlamlı değil (q > 0,3).
- **İddia çerçevesi:** Monarus'un "bias isabeti" rakamları doğru ölçülmüş olabilir, ama ölçtükleri şey bir öngörü gücü değil. Aynı mesafeye rastgele bir yön de aynı oranda ulaşıyor.

## 2. İşlem modelleri (havuz, NY17, maliyet sonrası)
Kazanç oranının başabaş noktası 1/(1+RR). Ayna: aynı anda ve aynı geometride ters yönlü işlem.

| Model | n | Kazanç oranı | Başabaş WR | Ayna WR | Medyan RR | Ort. R brüt | **Ort. R net** | Ayna farkı (q) | İddia |
|---|---|---|---|---|---|---|---|---|---|
| MA-T (bias + 1S konfirme) | 1.348 | %12,7 | %25,8 | %12,5 | 2,78 | +0,03 | **−0,05** | +0,04 (0,84) | — |
| ME-1 (bias + 4S CRT) | 2.165 | %28,3 | %37,6 | %30,1 | 1,98 | −0,01 | **−0,12** | −0,01 (0,96) | — |
| ME-1n (bias'sız, negatif kontrol) | 4.971 | %19,5 | %30,2 | %20,3 | 2,90 | −0,01 | −0,11 | −0,04 (0,65) | |
| ME-2 (haftalık bias + günlük CRT) | 764 | %27,5 | %36,9 | %28,4 | 2,04 | +0,03 | **−0,01** | +0,06 (0,82) | — |
| MF-1 (haftalık bias, kararsız pas) | 1.583 | %57,5 | %57,2 | %56,2 | 0,79 | +0,02 | **−0,10** | +0,03 (0,86) | WR %68–80 (filtreyle %80–85) |
| MF-1k (kararsızda devam) | 3.416 | %58,0 | %57,8 | %57,2 | 0,74 | +0,03 | −0,09 | +0,06 (0,53) | |
| MF-n (bias'sız, negatif kontrol) | 6.720 | %58,1 | %58,2 | %57,3 | 0,71 | +0,01 | −0,12 | +0,03 (0,70) | |
| MB-v (iddia 3 paritesi) | 928 | **%47,4** | %50 | %51,5 | 1,00 | −0,05 | **−0,17** | −0,08 (0,58) | WR ≥ %75, en yüksek %88 |
| MB-v (6 parite) | 2.229 | %49,1 | %50 | %49,6 | 1,00 | −0,02 | −0,15 | −0,01 (0,96) | |
| MB-s (SWMA yorumu, 6 parite) | 2.244 | %49,1 | %50 | %49,6 | 1,00 | −0,02 | −0,15 | −0,01 (0,95) | |
| MB-h0 (filtresiz marubozu) | 5.767 | %50,0 | %50 | %48,1 | 1,00 | −0,00 | −0,18 | +0,04 (0,47) | |
| MD-4S-a (1,8R filtreli) | **15** | %26,7 | %30,5 | %46,7 | 2,03 | −0,18 | −0,33 | — | WR %75, ayda 6–10R |
| MD-1G-a (1,8R filtreli) | **24** | %29,2 | %28,5 | %25,0 | 2,28 | −0,03 | −0,12 | — | |
| MD-4S-b / MD-1G-b (limit) | 21 / 18 | %28,6 / %27,8 | %27 / %24 | | 2,5 / 3,0 | +0,02 / +0,18 | −0,08 / +0,08 | (0,91 / 0,96) | |
| MD-4S-a-n1 (RR filtresiz) | 389 | %67,9 | %69,7 | %70,7 | 0,41 | −0,03 | **−0,09** | −0,08 (0,65) | |
| MD-1G-a-n1 (RR filtresiz) | 189 | %54,5 | %61,2 | %62,4 | 0,58 | −0,10 | −0,17 | −0,12 (0,70) | |
| MD-n0-a (POI'siz) | 460 | %28,9 | %27,0 | %26,3 | 2,46 | +0,09 | −0,06 | +0,09 (0,86) | |
| MC-A %1 (NQ, CISD) | 520 | %24,8 | %40 | %26,3 | 1,5 | −0,02 | **−0,03** | −0,09 (0,68) | 2026 sayımı ~%74 (OOS, bakılmadı) |
| MC-A %0,5 | 313 | %27,5 | %40 | %29,7 | 1,5 | −0,05 | −0,07 | −0,13 (0,66) | |
| MC-B %1 (engulf + limit) | 176 | %32,4 | %40 | %40,3 | 1,5 | −0,15 | −0,17 | −0,22 (0,54) | |

Notlar:
- **MC kazanç oranları neden düşük:** Kazanç oranı = süre sınırından (16:00 NY) önce TP'ye ulaşma. İşlemlerin bir kısmı açık kapanıyor ve piyasa değerinden sayılıyor; R'ye yansıyan budur.
  - Rastgele dakika ve yön H0'ı (500 tekrar) MC'yi geçiyor: permütasyon p = 0,62–0,96. MC rastgele girişten kötü ya da ona eşit.
  - BE varyantı (+1R'de stop girişe) kaybı biraz küçültüyor ama sonucu değiştirmiyor: ort. R net −0,02 ile −0,14 arası, hepsi negatif, hiçbiri anlamlı değil.
- **MB:** İddianın 3 paritesinin her birinde kazanç oranı %46–48. Maliyet 1R'lik hedefin ~%10'unu yiyor.
  - Trend + yapı + itki filtresi, filtresiz marubozuya (h0) göre bir şey eklemiyor.
- **MD:** 1,8R kuralı literal uygulanınca 7 enstrümanda 6 yılda 15–24 işlem kalıyor. Monarus ise ayda birden fazla işlem anlatıyor.
  - Kuralın gerçekte nasıl uygulandığı (hangi likidite) kodlanabilir biçimde anlatılmamış. Kapsam olarak bu not edilir; iddiayı kurtaran bir yol değildir.
  - RR filtresiz sürümde kazanç oranı %68 ve başabaş çizgisinin altında.
- **Yön, TR 00:00 sınırı, enstrüman alt kümeleri:** Ayna farkında düzeltmesiz p < 0,05 olan 24 hücre var. Bu, 623 testte şans eseri beklenen ~31'in altında.
  - Hiçbiri BH düzeltmesinden sağ çıkmıyor. Bunların 10'u negatif yönde.
  - Brüt en iyi hücreler (ör. ME-2 XAUUSD +0,30R, n = 101, p = 0,18) tek tek anlamlı bile değil.

## 3. Ağaç modeli + permutation importance (LOYO)
- OOF AUC: MF 0,74–0,76, ME 0,64, MD 0,54–0,59, MB 0,49–0,50, MC-A 0,56–0,61.
- **Önemli özniteliklerin hepsi geometrik:** RR ve stop/ATR (6/6 katlama).
  - Küçük RR'li işlemin TP'ye ulaşma olasılığı mekanik olarak daha yüksek. Model bu yüzden kazanan/kaybedeni ayırıyor, ama bu bir yön bilgisi değil.
  - Yön, saat, gün, ATR rejimi gibi öznitelikler önemsiz (MDA ~0).
- MB'de AUC 0,50: hiçbir öznitelik bilgi taşımıyor.

## 4. Doğrulama ve sızıntı
- **Testler:** 23/23 geçti.
  - SL-first, boşluk, dolum barı ve ayna işlem için birim testleri.
  - 11 model varyantı ve MC için pertürbasyon: karar anından sonraki fiyatlar bozulunca kesimden önceki olaylar birebir aynı.
  - MA bias'ı da kesimden sonraki veriden etkilenmiyor.
- **Örnek ay (MB, Aralık 2025 AUDUSD):** Videoda 11 işlem var, stoplar 5,9–13,8 pip. Kod 8 olay buluyor, stoplar 3,1–17,1 pip.
  - Videoda işlem saatleri olmadığı için birebir eşleştirilemedi. Veri kaynağı da farklı (FXCM / Dukascopy).
- **Ön kayıttan sapmalar ve açıklamalar** (karar günlüğünde):
  - MD kurulum ömrü kuralı. Olay sayısına bakılarak eklendi, sonuçlar görülmeden.
  - MB'de stopun girişin doğru tarafında olma şartı. Filtresiz varyantta sıfıra yakın riskli olaylar oluşuyordu; sonuçtan bağımsız bir geometri düzeltmesi.
  - MA ayna kontrolü: **post-hoc** (sonuç görüldükten sonra) eklendi; kontrol olarak raporlandı.
  - VWMA yerine SMA21 kullanıldı (spotta hacim yok). SWMA(26,5) için bir yorum kullanıldı.
- **Veri notu:** Yeni AUD ve JPY dosyalarında tatil günleri düz barlarla dolu, bu yüzden 25 Aralık gibi günler kalite filtresinden geçiyor. Etkisi küçük: yılda birkaç gün.

## 5. Kapsam (test edilmeyenler; iddiayı kurtaran yol değildir)
- **Kodlanmayan ya da ilk turda dışarıda bırakılan kurallar:**
  - MB'de FVG stop filtresi ve kâr sonrası geri çekilme işlemleri.
  - MF'nin 2. denemesi ve %50 + BE çıkışı.
  - MA-T'de limit giriş.
  - ME'de Key Level.
  - MD'de PDH/PDL/DXY kesişimi, haber filtresi ve "%20 inisiyatif".
  - MC'de konsolidasyon filtresi.
- **Monarus'un kendi indikatörleri ve veri kaynağı (FXCM/OANDA):** Bizim Dukascopy ile aynı değil. Gün ve 4S mum sınırı iki tanımla da (NY17, TR 00:00) denendi, sonuç değişmedi.
- **İspat yükü iddia sahibinde:** Bu kurallar videolarda anlatıldığı haliyle test edildi. Anlatılmayan bir filtre varsa, o anlatılana kadar test edilemez.

## 6. Deneme sayacı
- **2.233 test** (p-değeri) tek havuzda BH ve Bonferroni ile düzeltildi:
  - 748 işlem anahtarı × (R_net, ayna, gün sonu fazla getiri, BE),
  - MA 70 satır × 5 test,
  - MC H0 × 4.
- **Model × varyant:** 23 olay tanımı × 7 enstrüman × 2 gün sınırı (MB ve MC tek).
- **Bu tur öncesi yalnız olay sayısına bakılarak yapılan kontroller:** MD huni sayımı ve L = 5 TP pivotu. L = 5 istatistiğe girmedi.
