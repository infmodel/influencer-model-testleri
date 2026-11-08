# X thread taslağı (Monarus)

## 1/7 — görsel: `1_sonuc.png`

@TraderMonarus'un YouTube'da anlattığı 6 trade modelini (günlük bias, marubozu 1:1, fon sistemi, FVG ana modeli…) 6 yıllık gerçek veride test ettik.

Sonuç: Videolardaki kuralların hiçbiri kârlı değil. İddia edilen kazanma oranları çıkmıyor. 🧵

## 2/7

Nasıl test ettik?

33 içeriğin transkriptini taradık, 6 kilit videoyu yapay zekâya izlettik, kuralları koda döktük.

6 spot parite + altın + NQ, 2020–2025, 58.471 işlem. Maliyet dahil; aynı mumda stop ve hedef görülürse stop saydık. Kurallar sonuçtan önce kilitlendi.

## 3/7 — görsel: `2_iddia_olculen.png`

Marubozu 1:1: "%75 win rate'in hiç altına düşmedim … en fazla aldığım win rate de %88."

Aynı kurallar, iddianın 3 paritesi, 6 yıl, 927 işlem: %47.

6 aylık dönemlerin en iyisi %61. 17 işlemlik serilerin en iyisi %76,5. %88'e hiç ulaşılmıyor.

## 4/7

"Fon sistemi": iddia %68–80. Ölçülen %57,5. Hedef stoptan yakın olduğu için başa baş zaten %57 → net zarar.

Ana model (FVG + 30dk, min 1,8R): iddia %75, ayda 6–10R. Kural aynen uygulanınca 7 enstrümanda 6 yılda sadece 15 işlem çıkıyor.

## 5/7 — görsel: `3_bias_isabeti.png`

Günlük bias isabeti (%60–80) rakam olarak doğru: biz de %64–68 bulduk.

Ama ters yönde aynı mesafedeki seviyeye değme oranı da aynı (%68–74). Hedef kapanışa çok yakın. Yani bu oran yön bilgisi değil; bias yönünde gün sonu getirisi sıfır.

## 6/7 — görsel: `4_backtest.png`

Backtest: 260 satırın hiçbiri önceden yazılmış kârlılık şartını geçemedi.

Bias filtresi eklemek de bir şey değiştirmiyor: filtreli ve filtresiz sürümler aynı sonucu veriyor. Maliyeti sıfır alsak bile sonuç başa baş civarında.

## 7/7

Notlar:
- 2026 verisine dokunmadık.
- Test edilen şey videolarda öğretilen kurallar. Anlatılmayan bir takdir varsa bu oranları o savunmalı; ispat yükü iddia sahibinde.
- Kod, testler, her işlem ve kural kaynakları (video + dakika) açık: <GitHub linki>
