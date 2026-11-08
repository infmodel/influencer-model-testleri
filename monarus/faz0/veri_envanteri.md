# Monarus Faz 0 (ön): veri envanteri ve model eşlemesi (7 Kasım 2026)

Kaynak: `../../data/CLAUDE.md` (kullanıcı onayıyla okundu). Yalnızca yapı (kolonlar, satır sayısı) kontrol edildi; fiyatlara bakılmadı. IS = 2020-01-01 – 2025-12-31. 2026 karışık dosyalarda `is_oos_2026` / `adj_segment` ile kesilecek.

## Eldeki veri → Monarus enstrümanları

| Monarus | Bizde | Kaynak | Not |
|---|---|---|---|
| EURUSD | ✓ spot | Dukascopy 1dk | Tek fiyat serisi (bid/mid doğrulanmadı) |
| GBPUSD | ✓ spot | Dukascopy 1dk | |
| USDCAD | ✓ spot | Dukascopy 1dk | |
| USDCHF | ✓ spot | Dukascopy 1dk | |
| AUDUSD | ✓ spot | Dukascopy 1dk bid, `data/FX_Currencies/dukascopy_spot/` (8 Kas eklendi) | 6A vadeli yalnız çapraz kontrol |
| USDJPY | ✓ spot | Dukascopy 1dk bid, `data/FX_Currencies/dukascopy_spot/` (8 Kas eklendi) | 6J vadeli (1/x) yalnız çapraz kontrol |
| XAUUSD | ~ vadeli | GC 1dk | `*_adj` puan bazlı, yüzde işi için `ret_1m` |
| XAGUSD | ✗ | — | Yok |
| BTCUSD | ✗ | — | Yok |
| NQ | ✓ vadeli | NQ 1dk, `datetime_ny` | `Dreyko/faz0/dreyko_data.py` `load_is()` session_date düzeltmesiyle |

## Model bazında kapsam

| Model | Gereken | Kapsam |
|---|---|---|
| MA | Günlük (1dk'dan TR 00:00 = 21:00 UTC ve NY 17:00 sınırıyla yeniden örneklenir) + 1S | EURUSD, GBPUSD, USDCAD, USDCHF (spot); AUDUSD, USDJPY, altın (vadeli, ikincil). 6 yıl (iddia 20+ yıl) |
| MB | 15dk | GBPUSD (spot), AUDUSD (6A), USDJPY (6J ters). İddianın 3 paritesinin hepsi var; 2'si vadeli |
| MC | NQ 15dk | Tam |
| ME | 4S (TR 00/04/08/12/16 = UTC 21/01/05/09/13) + günlük + haftalık | MA ile aynı set |
| MD | 1G/4S FVG + 30dk | MA ile aynı set (Gemini pencere 2 sonrası) |

## Notlar
- TR sabit UTC+3 (2016'dan beri DST yok): TR 00:00 = 21:00 UTC her zaman. NY 17:00 = 21:00 UTC (yaz) / 22:00 UTC (kış). İki gün sınırı yılın ~yarısında aynı.
- Maliyet (data/CLAUDE.md §8): spot EURUSD 1.0, GBPUSD 1.3, USDCAD/USDCHF 1.5 pip RT; 6A/6J $5 RT + 1 tick/taraf; NQ $4 + 1 tick.
- Tam Faz 0 (eksik bar, hafta sonu/tatil, yeniden örnekleme testleri, spot↔vadeli tutarlılık) kod aşamasında `faz0/` altında yapılacak.

**8 Kasım güncellemesi:** AUDUSD ve USDJPY için spot veri indirildi (bkz. `faz0_rapor.md` §9). Gün sınırında ana test NY 17:00.
