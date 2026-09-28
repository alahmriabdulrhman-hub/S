# رسوم التمويل الفعلية لعقود باينانس (USDT) من 2020، وأسعار السوق الفوري بالساعة 2024–2026
import io, zipfile, datetime as dt, urllib.request, os, gzip, csv
from concurrent.futures import ThreadPoolExecutor
SYMS = sorted({f[:-7] for f in os.listdir("data") if f.endswith(".csv.gz")})
B = "https://data.binance.vision/data"
def months(y0, m0, y1, m1):
    y, m = y0, m0
    while (y, m) <= (y1, m1):
        yield f"{y}-{m:02d}"; m += 1
        if m == 13: y, m = y + 1, 1
def get(url):
    try:
        with urllib.request.urlopen(url, timeout=60) as r: return r.read()
    except Exception: return None
def rows_of(blob):
    out = []
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for n in z.namelist():
            for row in csv.reader(io.TextIOWrapper(z.open(n))):
                if row and row[0][:1].isdigit(): out.append(row)
    return out
def funding(sym):
    p = f"{sym}USDT"; rows = []
    for mo in months(2020, 1, 2026, 8):
        b = get(f"{B}/futures/um/monthly/fundingRate/{p}/{p}-fundingRate-{mo}.zip")
        if b: rows += [(int(r[0]), r[2]) for r in rows_of(b)]
    if rows:
        os.makedirs("funding", exist_ok=True)
        with gzip.open(f"funding/{sym}.csv.gz", "wt", newline="") as f:
            w = csv.writer(f); w.writerow(["time", "rate"]); w.writerows(sorted(set(rows)))
    return sym, len(rows)
def spot(sym):
    base = sym[4:] if sym.startswith("1000") else sym
    p = f"{base}USDT"; rows = []
    for mo in months(2024, 1, 2026, 8):
        b = get(f"{B}/spot/monthly/klines/{p}/1h/{p}-1h-{mo}.zip")
        if b: rows += [(int(r[0]) // (1000 if int(r[0]) > 1e14 else 1), r[4], r[7]) for r in rows_of(b)]
    d = dt.date(2026, 9, 1)
    while d <= dt.date(2026, 9, 27):
        b = get(f"{B}/spot/daily/klines/{p}/1h/{p}-1h-{d}.zip")
        if b: rows += [(int(r[0]) // (1000 if int(r[0]) > 1e14 else 1), r[4], r[7]) for r in rows_of(b)]
        d += dt.timedelta(days=1)
    if rows:
        os.makedirs("spot", exist_ok=True)
        with gzip.open(f"spot/{sym}.csv.gz", "wt", newline="") as f:
            w = csv.writer(f); w.writerow(["open_time", "close", "quote_volume"]); w.writerows(sorted(set(rows)))
    return sym, len(rows)
with ThreadPoolExecutor(12) as ex:
    for s, n in ex.map(funding, SYMS): print("funding", s, n, flush=True)
    for s, n in ex.map(spot, SYMS): print("spot", s, n, flush=True)
