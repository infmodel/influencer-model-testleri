# Influencer trade modelleri: gerçek veride test

Sosyal medyada (çoğunlukla YouTube) anlatılan gün içi trade modellerini koda döküp gerçek vadeli işlem verisinde test ediyoruz. Soru tek: **Model, anlatıldığı haliyle uygulandığında avantaj sağlıyor mu?**

- Kurallar influencer'ın kendi videolarından çıkarılır. Her kuralın hangi videonun hangi dakikasından alındığı proje klasöründe listelenir.
- Kurallar ve başarı şartları sonuçlar görülmeden kayda geçer (ön kayıt).
- Kod, testler, raporlar ve işlem listeleri açıktır. Ham fiyat verisi lisans gereği paylaşılmaz; aynı veriye sahip olan herkes sonuçları yeniden üretebilir.

## Projeler

| Proje | Model | Veri | Sonuç | Klasör |
|---|---|---|---|---|
| Dreyko | 09:30 manipülasyonu, First Presented FVG, IFVG, Turtle Soup + CISD, NQ/ES SMT | CME NQ ve ES 1 dk, 2020–2025 | **Avantaj bulunamadı.** 32 kural varyantının hiçbiri başarı şartını geçmedi, filtresiz kuralların hepsi maliyet sonrası zararda | [`dreyko/`](dreyko/) |

## Nasıl test ediyoruz?

Ayrıntı: [`METODOLOJI.md`](METODOLOJI.md). Kısaca:

1. **Kuralları çıkar:** Kanalın video transkriptleri taranır, model anlatan videolar ayrıca izlenip kurallar (saat, giriş, stop, hedef, filtreler) yazılır.
2. **Kodla ve doğrula:** Her kural için birim testi; "gelecek veri sızıntısı" testi; kodun, influencer'ın videoda gösterdiği örnek işlemi yakalayıp yakalamadığı kontrol edilir.
3. **Olay çalışması:** Kurulum oluştuktan sonra fiyat nereye gidiyor? İki yönlü, çoklu test düzeltmeli.
4. **Backtest:** Önceden kilitlenmiş varyantlar, aynı mumda stop ve hedef görülürse stop, komisyon ve kayma dahil, rastgele yön permütasyon testi.
5. **Kilitli OOS:** 2026 verisi en baştan ayrılır. Bir model IS'te geçemezse OOS'a hiç bakılmaz.

## Yapay zekâ kullanımı

Transkript taraması, video analizi (Gemini) ve kod yazımı yapay zekâ desteğiyle yapıldı. **Sonuçlar bir yapay zekânın yorumu değildir:** gerçek fiyat verisi üzerinde çalışan, testleri yazılmış kodun hesapladığı sayılardır. Kod açık; kuralların videolardan doğru çıkarılıp çıkarılmadığı kaynak tablosundan, kodun doğru çalışıp çalışmadığı testlerden ve işlem listelerinden kontrol edilebilir.

## Neler paylaşılmıyor?

- **Ham fiyat verisi:** Databento lisansı gereği. Veriyi kendiniz edinip aynı kodu çalıştırabilirsiniz (proje README'lerinde "Yeniden üretme" bölümü).
- **Video transkriptleri:** Telif nedeniyle. Kaynak tablolarında video linki, dakika ve kısa alıntı var; transkripti indiren script paylaşılıyor.

## Kurulum

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest dreyko
```

Birim testlerinin bir kısmı gerçek veri ister; veri yoksa o testler hata verir. Veri yolu `TRADE_DATA_DIR` ortam değişkeniyle verilir.

## Düzeltme ve itiraz

Bir kural yanlış ya da eksik kodlandıysa issue açın. Kuralın **yazılı ve test edilebilir** tanımını ve kaynağını (video + dakika) verin; aynı veride aynı yöntemle test edilir ve sonuç ne çıkarsa yayınlanır.

## Lisans

Kod: MIT ([`LICENSE`](LICENSE)). Bu repo yatırım tavsiyesi değildir.
