"""Dukascopy BID 1dk bi5 indirici. Devam edebilir: var olan dosyayi atlar. Kullanim:
python3 indir.py SEMBOL BASLANGIC BITIS CIKTI_KLASOR   (tarihler YYYY-MM-DD, dahil)"""
import sys, os, time, datetime as dt, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
sym, a, b, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
# 2026 = kilitli OOS. Yalnız kullanıcı onayıyla (8 Kas 2026: "2026 verisi de olsun elimizde")
# OOS_IZIN=1 ile ve ayrı yıl dosyasına indirilir; fiyatlarına bakılmaz, IS yükleyicileri okumaz.
assert b <= "2025-12-31" or (os.environ.get("OOS_IZIN") == "1" and a >= "2026-01-01"), "2026 yasak (kilitli OOS)"
d0, d1 = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
days = [d0 + dt.timedelta(i) for i in range((d1 - d0).days + 1)]
if os.environ.get("ATLA_CMT"): days = [d for d in days if d.weekday() != 5]  # cumartesi: mevcut ham dosyada yok, atla
UA = {"User-Agent": "Mozilla/5.0"}
def get(d):
    p = f"{out}/{sym}/{d.year}/{d.month:02d}/{d.day:02d}.bi5"
    if os.path.exists(p): return d, "var"
    url = f"https://datafeed.dukascopy.com/datafeed/{sym}/{d.year}/{d.month-1:02d}/{d.day:02d}/BID_candles_min_1.bi5"
    for k in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                data = r.read()
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p + ".tmp", "wb") as f: f.write(data)
            os.replace(p + ".tmp", p)
            return d, f"ok{len(data)}"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p + ".404", "w").close()  # kalici yok isareti
                return d, "404"
            time.sleep(2 * (k + 1) * (3 if e.code == 429 else 1))
        except Exception:
            time.sleep(2 * (k + 1))
    return d, "HATA"
def get_skip(d):
    p = f"{out}/{sym}/{d.year}/{d.month:02d}/{d.day:02d}.bi5.404"
    if os.path.exists(p): return d, "404"
    return get(d)
bad = []
with ThreadPoolExecutor(int(os.environ.get("NT","4"))) as ex:
    for i, (d, s) in enumerate(ex.map(get_skip, days)):
        if s == "HATA": bad.append(d)
        if i % 200 == 0: print(i, d, s, flush=True)
print("BITTI", sym, "hata:", [str(x) for x in bad])
