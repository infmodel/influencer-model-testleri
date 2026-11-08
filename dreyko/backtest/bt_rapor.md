# Dreyko — backtest raporu (kullanıcı kararıyla, Adım 0 sonrası sapma)

**Tarih:** 7 Kasım 2026 · **Veri:** IS 2020–2025, NQ (kural) + ES (aynen) · **Kurallar:** `../karar_gunlugu.md` "Backtest" (sonuçlardan önce yazıldı) · **Kod:** `bt.py`, `run_bt.py`, `test_bt.py` (7/7) · **Çıktılar:** `out/results_*.csv`, `out/trades_*.parquet`

## Sonuç: NO-GO

- NQ'da 32 varyantın hiçbiri ön kayıtlı GO şartını sağlamadı. GO şartı: ortalama, medyan ve NoTop2 pozitif + permütasyon q<0.05 + en az 4/6 kârlı yıl + ES'de pozitif.
- NQ'da en küçük permütasyon q-değeri 0.72.
- Filtresiz temel kuralların hepsi maliyet sonrası zararda. 1 kontratla 6 yılda NQ'da −$3K ile −$74K, ES'de −$9K ile −$70K arası.

## NQ özet tablo (1 kontrat, maliyet dahil)

| Hipotez | Hedef | Filtre | n | İsabet | Ort. R | PF | Net $ | Max DD $ | Kârlı yıl | perm q |
|---|---|---|---|---|---|---|---|---|---|---|
| H1-A FPFVG | L | filtresiz | 878 | %50 | −0.01 | 0.98 | −21.7K | 47.7K | 2/6 | 0.72 |
| H1-A FPFVG | R | filtresiz | 1372 | %36 | +0.01 | 1.01 | −22.5K | 82.0K | 3/6 | 0.72 |
| H1-B FPFVG | L | filtresiz | 783 | %50 | −0.02 | 0.97 | −16.4K | 43.9K | 2/6 | 0.72 |
| H1-B FPFVG | R | filtresiz | 1217 | %36 | −0.00 | 1.00 | −26.7K | 84.4K | 2/6 | 0.73 |
| H2 IFVG | L | filtresiz | 1416 | %41 | −0.02 | 0.97 | −44.0K | 68.3K | 4/6 | 0.84 |
| H2 IFVG | R | filtresiz | 1432 | %34 | −0.05 | 0.92 | −74.4K | 85.2K | 1/6 | 0.84 |
| H2b TS+CISD | L | filtresiz | 830 | %38 | +0.06 | 1.10 | −3.1K | 42.7K | 4/6 | 0.72 |
| H2b TS+CISD | R | filtresiz | 839 | %37 | −0.01 | 0.98 | −36.4K | 44.1K | 2/6 | 0.73 |
| **En iyi NQ:** H2 | L | SMT+makro | 52 | %42 | +0.29 | 1.53 | +7.8K | 5.0K | 4/6 | 0.72 |

- **"En iyi" satır neden geçmiyor:** Medyan R −1.0; işlemlerin çoğu stopla kapanıyor ve kâr birkaç büyük işlemden geliyor. Örneklem 6 yılda 52 işlem, permütasyon p=0.28. 32 varyant arasından seçildiği için iyimser.
- **R ile $ farklı işaret verebilir:** Ortalama R, dar stoplu işlemlerin büyük R'lerinden etkileniyor; $ sabit 1 kontrat. Örnek H2b L: +0.06R ama −$3.1K.
- **Başabaş maliyet:** Filtresiz varyantlarda işlem başı brüt kazanç −1.9 ile +0.5 puan arası. NQ'nun gerçek maliyeti 0.70 puan; yani maliyet sıfır olsa bile çoğu varyant ancak başabaş.

## ES (NQ'da kurulan kurallar aynen)

- Filtresiz 8 varyantın hepsi zararda (−0.05 ile −0.15 R, 0–2/6 kârlı yıl).
- **Tek dikkat çeken hücre:** H1 + SMT + makro. 4 varyantın hepsi pozitif (+0.12 ile +0.76 R, n=23–47, 4–6/6 kârlı yıl), ama en iyi q=0.061. Aynı filtre NQ'da negatif (−0.04 ile −0.26 R). Kurallar NQ'da kurulup ES'de tekrar edilmeliydi; burada tersi oluyor ve n çok küçük. Ön kayıtlı kurala göre bulgu değil.

## Duyarlılık ve denetim

- **Limit dolumu:** "Dokunuşta dolum" (daha iyimser) H1'i değiştirmiyor: −0.01 ile +0.01 R, 2–3/6 kârlı yıl.
- **Permütasyon notu:** Aynı giriş, aynı stop/hedef mesafesi, rastgele yön. H1'de gerçek yön, ters yönden biraz iyi (filtresiz L için p≈0.05). Ama ters yön de zararda; yön bilgisi maliyeti karşılamıyor.
- **Elle doğrulama:** İki rastgele işlem ham barlarla birebir doğrulandı:
  - 12 Mayıs 2023 H1 short: dolum 13471.00, hedef 09:48'de, R=+1.00.
  - 6 Mayıs 2021 H2 long: stop 10:00'da, R=−1.01.

## Deneme sayacı

Proje toplamı: 1200 p-değeri (Adım 0 + seçicilik turu) + 64 backtest varyantı + 4 duyarlılık.
