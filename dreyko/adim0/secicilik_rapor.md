# Dreyko — seçicilik turu raporu (Adım 0 devamı, backtest değil)

**Tarih:** 7 Kasım 2026 · **Veri:** NQ ve ES 1dk, IS 2020–2025 · **Ön kayıt:** `../karar_gunlugu.md` ("Seçicilik turu", sonuçlardan önce yazıldı) · **Kod:** `secicilik.py`, `run_secicilik.py`, `test_secicilik.py` (tüm testler 14/14 geçti, sızıntı testi dahil) · **Ham çıktılar:** `out/secicilik_*.csv`

## 1. Sonuç: ön kayıtlı geçme kuralı sağlanmadı → NO-GO

- **Birincil aile** (F1∧F2 "A+ kurulum", 7 olay, 12:00 getirisi): NQ'da en küçük q = **0.27**, ES'de **0.96**. Geçmek için q<0.05 gerekiyordu.
- **İkincil aile** (145 test/enstrüman): en küçük q NQ'da 0.98, ES'de 0.59. Geçme kuralına uyan hücre yok (q<0.05 ve NQ–ES aynı işaret). Bu yüzden gölge izleme adayı da çıkmadı.

## 2. Filtreler (Dreyko'nun kurallarından, ön kayıtlı)

| Filtre | Tanım | Kaynak |
|---|---|---|
| F1: key level manipülasyonu | İşlem yönünün tersindeki A+ seviyelerinden biri (Asya H/L veya PDH/PDL) 09:30'a kadar alınmamış, 09:30 ile giriş arasında alınmış | "3 şart" (key level + manipülasyon); ön koşul (b) |
| F2: açık A+ draw | İşlem yönündeki A+ seviyelerinden biri girişe kadar alınmamış | "Hedef A+ draw"; "09:30'da hedefe yakınsa işlem yok" |
| F3: Asya konsolide | Asya range'i / ATR, geçmiş günlerin medyanının altında | QMr3 |

Ne kadar seçici oldukları (NQ):
- **F1:** FPFVG olaylarının ~%2'si, IFVG'nin %14'ü, TS+CISD'nin %19'u. Bu oran Dreyko'nun "her gün kurulum yok" sözüyle uyumlu.
- **F2 ve F3:** Olayların %60–75'inde var.
- **F1∧F2 kurulum sayısı (6 yılda):** FPFVG 17–25, IFVG 151, TS+CISD 122. Bu yaklaşık ayda 2 kurulum ediyor; Dreyko "ayda 4–5" diyor.

## 3. Birincil aile (F1∧F2, 12:00, doğal yönde, ATR)

| Olay | NQ n | NQ ort. | NQ medyan | NQ t | NQ q | ES n | ES ort. | ES t |
|---|---|---|---|---|---|---|---|---|
| FPFVG_form_A | 25 | +0.104 | +0.084 | 1.81 | 0.27 | 21 | +0.062 | 0.87 |
| FPFVG_form_B | 20 | +0.071 | +0.074 | 1.18 | 0.35 | 16 | +0.033 | 0.40 |
| FPFVG_retest_A | 23 | +0.120 | +0.093 | 1.96 | 0.27 | 17 | −0.003 | −0.05 |
| FPFVG_retest_B | 17 | +0.096 | +0.093 | 1.36 | 0.34 | 14 | +0.012 | 0.14 |
| IFVG | 151 | −0.017 | −0.055 | −0.56 | 0.58 | 118 | −0.005 | −0.15 |
| SWEEP | 39 | −0.095 | −0.156 | −1.60 | 0.27 | 28 | +0.048 | 0.49 |
| TSCISD | 122 | +0.020 | −0.008 | 0.66 | 0.58 | 95 | −0.018 | −0.65 |

**Okuma:**
- **Dreyko'nun asıl kurulumu** (key level süpürülür, IFVG veya TS+CISD ile dönülür, hedef açık A+ draw) en çok örneği olan iki satır: n=151 ve n=122. İkisinde de etki yok. IFVG'de medyan negatif, isabet %44.
- **NQ'da A+ filtreli FPFVG satırları** pozitif (+0.07…+0.12 ATR). NQ'da medyan MFE 0.24, MAE 0.14–0.18. Ama:
  - örneklem yılda ~4 işlem,
  - t<2,
  - ES'de tekrarlanmıyor: retest −0.003, MFE ≈ MAE.

  Ön kayıtlı kurala göre bu bir bulgu değil ve gölge izleme adayı da sayılmaz.
- **"3 şart" (F1∧SMT):** 9–40 olayla istatistik yapılamayacak kadar seyrek.

## 4. Sağlamlık ve uyarılar

- **Bu tur, filtresiz Adım 0 sonuçları görüldükten sonra yapıldı.** Filtreler Dreyko'nun kendi kurallarından alındı ve sonuçlardan önce kilitlendi, ama tur yine de post-hoc. İleride başka filtre denenirse her deneme sayaca eklenmeli.
- **Kodlanmayan katman:** 4sa/günlük FVG, OB ve haftalık gap gibi key level'lar bu turda yok. Bunlar görsel ve takdirî seçim gerektiriyor; mekanikleştirmek yeni hipotez sayılır.
- **Sızıntı testi:** Giriş anından sonraki barlar ±%2 + 50 puan bozulduğunda, 200'den fazla gerçek olayın F1/F2/F3 bayrakları değişmedi.

## 5. Toplam deneme sayısı (Dreyko projesi)

| Tur | Test sayısı |
|---|---|
| Adım 0 | 896 p-değeri + 7 ağaç modeli |
| Seçicilik turu | NQ ve ES için 7 birincil + 145 ikincil = 304 p-değeri |
| **Toplam** | **1200 p-değeri** |

Düzeltme öncesi ham p<0.05 sayısı, şansla beklenen düzeyde.
