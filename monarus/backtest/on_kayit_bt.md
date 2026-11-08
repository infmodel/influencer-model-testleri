# Backtest ön kaydı (Monarus) — sonuçlardan ÖNCE, 2026-11-08

**Sapma:** Adım 0'da hiçbir sinyal geçmedi ve önerim backtest yapılmamasıydı. Kullanıcı yine de istedi: "burda amaç kullanabileceğim sistemler bulmak değil influencerlerin ne kadar yalancı olduğunu görmek".
- Bu yüzden backtest bir **iddia testidir**, sistem seçimi değildir. Sonuçlara bakarak kural, eşik, enstrüman ya da varyant değiştirilmez. Hiçbir sonuç canlıya aday olarak sunulmaz.
- Rapor dili: kanıtlanan şeyle sınırlıdır (İnfModel/CLAUDE.md). Hüküm yazılmaz ("yalancı" gibi); iddia rakamıyla ölçülen rakam yan yana konur.

## Kurallar
- **Olaylar:** Adım 0'daki 23 tanımın hepsi, aynen (`adim0/m_*.py`). Kullanıcı kararı: "Adım 0'daki tüm varyantlar".
  - Ek olarak MC'nin BE varyantı ayrı anahtar olarak alınır (MC-*-BE).
  - Enstrümanlar ve gün sınırları Adım 0 ile aynı. Yalnız IS 2020–2025.
- **Sıralı işlem:** Model × varyant × enstrüman × gün sınırı başına aynı anda tek açık pozisyon. Bir işlem kapanmadan gelen olay atlanır.
  - Kapanış: TP, stop ya da süre sınırı.
  - Süre sınırları Adım 0 ile aynı: MB/MD/MF 5 gün, MA-T/ME-1 gün sonu, ME-2 hafta sonu, MC 16:00 NY.
- **Boyutlama:** Her işlem 1R (sabit risk). Sonuçlar R cinsinden; birleşik getiri yok. Kullanıcı kararı.
- **Simülasyon:** SL-first.
  - Boşlukla açılış stopun ötesindeyse açılıştan çıkılır.
  - Limit/stop dolum barında TP sayılmaz.
  - Maliyet data/CLAUDE.md'den; AUD/JPY spot için geçici 1,3 pip.
- **"Ana enstrüman" ve "aynen deneme":** Kurallar Monarus'tan dondurulmuş geldiği için kalibrasyon yok.
  - Ana enstrüman: FX modellerinde GBPUSD (MB'de iddianın 3 paritesi birlikte de raporlanır), MC'de NQ. Diğer enstrümanlar genelleme olarak raporlanır.

## Ölçülenler (her anahtar)
1. **İşlem ve isabet:** n, yılda işlem, kazanç oranı (WR) ve Wilson %95 GA, başabaş WR.
2. **R dağılımı:** ortalama / medyan R_net, NoTop2 (en iyi 2 işlem çıkarılınca toplam R), toplam R, ayda ortalama R, PF.
3. **Zaman tutarlılığı:** kârlı yıl / çeyrek sayısı, en büyük drawdown (R), en uzun sualtı süresi (gün).
4. **Yön:** long ve short ayrı.
5. **Maliyet merdiveni:** 0×, 0,5×, 1×, 2× maliyet ve başabaş maliyet (pip).
6. **Rastgele giriş permütasyonu (200 tekrar):** Her işlemin günü korunur. Model penceresinde rastgele dakika ve rastgele yön seçilir; aynı stop mesafesi, aynı RR ve aynı süre sınırı kullanılır.
   - Pencereler: MB 08–18 TR, MD 09–17 TR, MA-T 09–19 TR, MC 09:30–13:00 NY, diğerlerinde tüm gün.
   - Ölçülen: ortalama R_net'in rastgele dağılımdaki yeri (z, p).
7. **Monte Carlo:** İşlem sırası 1.000 kez karıştırılır. En büyük drawdown ve en uzun kayıp serisi için %95 / %99.
8. **Deflated Sharpe (işlem başına):** Deneme sayısı N = bu backtest'teki anahtar sayısı.
9. **İddia kıyası (aylık sayım, Monarus'un kendi sayım biçimi):**
   - **MB:**
     - Ay ay WR; WR'si ≥ %75 olan ayların oranı.
     - 5–6 aylık kayan pencerelerde WR'nin en düşüğü ve en yükseği ("%75'in altına düşmedim").
     - 17 ardışık işlemlik pencerelerde en yüksek WR ve %88'e ulaşma sıklığı (iddia: 17 işlemde %88,24).
   - **MF:** WR'nin %68–80 bandıyla kıyası.
   - **MD:** WR (%75 iddiası) ve aylık R ("ayda 6–10R").
   - **MC:** Aylık TP/stop sayımı (iddianın kendisi 2026'da, burada yalnız IS dağılımı).

## Okuma barajları (sonuçtan önce)
- **"Kurallar kârlı":** Ana alt kümede (tümü) şunların hepsi:
  - ortalama R_net > 0, medyan R_net > 0 (RR ≥ 1 modellerde ortalama ve NoTop2 yeterli),
  - NoTop2 > 0,
  - permütasyon p < 0,05,
  - DSR > 0,95,
  - en az 4/6 yıl kârlı,
  - başabaş maliyet ≥ 2 × varsayılan maliyet.
- **"İddia ile tutarlı":** İddia edilen WR, ölçülen WR'nin %95 güven aralığı içinde. Aralığın üstündeyse "iddia bu kurallarla üretilemiyor".
