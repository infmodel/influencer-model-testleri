# Spot FX verisini Dukascopy'den indirme

Bu projedeki altı spot paritenin (EURUSD, GBPUSD, USDCAD, USDCHF, AUDUSD, USDJPY) kaynağı Dukascopy'nin herkese açık datafeed'idir: günlük `BID_candles_min_1.bi5` dosyaları, 1 dakikalık BID mumları. Ham veri paylaşılmaz; bu script'lerle aynı veriyi kendiniz indirebilirsiniz.

| Script | Ne yapar |
|---|---|
| `indir.py SEMBOL BAŞLANGIÇ BİTİŞ KLASÖR` | Günlük bi5 dosyalarını indirir (devam edebilir; var olanı atlar). 2026 bilerek kilitli: yalnız `OOS_IZIN=1` ile |
| `decode.py` | bi5 çözücü: LZMA, kayıt `>IIIIIf` (zaman sn, open, close, low, high, hacim) |
| `donustur.py` | Günlük dosyaları ham parquet biçimine çevirir; hafta sonu kuralı (Cuma 17:00 NY sonrası ve Cumartesi atılır, Pazar açılış öncesi düz barlar ilk hacimli barın kapanışıyla dolar) |
| `build.py SEMBOL POINT ONDALIK İNDİRME_KLASÖRÜ ÇIKTI` | Yıllık `sembol_YYYY.parquet` dosyalarını yazar |
| `kontrol.py` | Sıralama, mükerrer, NaN, High<Low, fiyat aralığı, boşluk kontrolleri |
| `islenmis.py` | Ham yıllık dosyalardan `fx_dukas_<pair>_1m_processed.parquet` ve günlük özet üretir (ATR, PDH/PDL, `is_oos_2026`, saat kolonları) |
| `dogrula_eurusd.py`, `dogrula_donusum.py` | Yöntem doğrulaması: indirilen EURUSD günleri mevcut dosyayla dakika dakika karşılaştırılır |

**Doğrulama:**
- EURUSD 2023'ten 66 gün (82.260 dakika) mevcut ham dosyayla %100 birebir aynı çıktı.
- `islenmis.py`, mevcut EURUSD işlenmiş dosyasını (2.547.215 satır, 32 kolon) birebir yeniden üretti.

**Örnek:**
```bash
python indir.py AUDUSD 2020-01-01 2025-12-31 ham/
python build.py AUDUSD 1e-5 5 ham/ raw/        # USDJPY: 1e-3 3
python kontrol.py raw audusd 0.55 0.82
python islenmis.py raw/ processed/ audusd
```

**Not:**
- Dukascopy sunucusu IP başına hız kısıtlaması uyguluyor: ilk ~60 dosyadan sonra 503 dönüyor, istek başına 5–40 sn. Eşzamanlılık `NT` ortam değişkeniyle (varsayılan 4) ayarlanır.
- Tatil günlerinde Dukascopy düz barlar (O=H=L=C) verir; bunlar korunur.
