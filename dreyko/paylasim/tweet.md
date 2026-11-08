# Twitter thread taslağı (Dreyko)

## 1/7  — görsel: `1_sonuc.png`  (241 karakter)

Dreyko'nun sıfırdan başlayanlar için YouTube'da herkese açık bir eser olarak sunduğu trade modelini 6 yıllık gerçek NQ/ES verisinde test ettik.

Sonuç: Videolarda anlatılan kurallarla sistematik bir avantaj yok. Maliyetler düşülünce zarar. 🧵

## 2/7  — görsel: `2_yontem.png`  (262 karakter)

Nasıl test ettik?

67 videonun transkriptini taradık, 11 kilit videoyu yapay zekâya izlettik. 09:30 manipülasyonu, FPFVG, IFVG, Turtle Soup + CISD, NQ/ES SMT ve makro saatlerini koda döktük.

Kod, Dreyko'nun 4 Haziran 2025 canlı işlemini aynı kurulumla yakaladı.

## 3/7  — görsel: `3_olay_calismasi.png`  (250 karakter)

1. sınav: Kurulumdan sonra fiyat nereye gidiyor?

Cevap: İki yöne eşit. Öğlene kadar ortalama getiri her kurulumda sıfır civarında.

İlk FVG günlerin %99.7'sinde oluşuyor, yani seçici bir sinyal değil. 1.200+ testte, düzeltme sonrası 0 anlamlı sonuç.

## 4/7  (229 karakter)

2. sınav: Dreyko'nun kendi filtreleri.

Asya / önceki gün high-low süpürmesi, açık A+ hedef, Asya konsolidasyonu ve "3 şart" (key level + SMT + manipülasyon). Kuralları sonuca bakmadan kilitledik.

Hiçbiri anlamlı fark yaratmadı.

## 5/7  — görsel: `4_backtest.png`  (225 karakter)

3. sınav: Backtest.

32 varyant, 1 kontrat, komisyon + kayma dahil. Aynı mumda stop ve hedef görülürse stop saydık.

6 temel kuralın 6'sı da 6 yıl sonunda zararda: −$3K ile −$74K arası. Hiçbir varyant başarı şartını geçemedi.

## 6/7  (259 karakter)

Neyi test ettik? YouTube serisinde öğretilen kuralları. Yani videoları izleyip sistemi öğrenme vaadini.

Asıl iş videolarda öğretilmeyen bir takdirdeyse, videolar zaten yeterli değil demektir. Hiçbir videoda win rate, işlem sayısı ya da maliyet gösterilmiyor.

## 7/7  (255 karakter)

Notlar:
- 2026 verisine dokunmadık; kurallar sonuçlardan önce kilitlendi.
- Kod birim testlerinden ve sızıntı (lookahead) testinden geçti.
- Videolardaki tek günlük örnekler istatistik değildir. Bir model ancak yüzlerce günde test edilince bir şey söyler.
