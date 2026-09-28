# تحديث أسبوعي للبيانات: أسعار الساعة (عقود + فوري)، رسوم التمويل، إعلانات باينانس
import io, zipfile, csv, gzip, os, json, time, datetime as dt, urllib.request, glob
from concurrent.futures import ThreadPoolExecutor
B = "https://data.binance.vision/data"
UA = {"User-Agent": "Mozilla/5.0"}
TODAY = dt.date.today()
def get(url, timeout=60):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r: return r.read()
    except Exception: return None
def rows_of(blob):
    out = []
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for n in z.namelist():
            for r in csv.reader(io.TextIOWrapper(z.open(n))):
                if r and r[0][:1].isdigit(): out.append(r)
    return out
def read_gz(path):
    with gzip.open(path, "rt") as f:
        rd = csv.reader(f); head = next(rd); return head, [r for r in rd]
def write_gz(path, head, rows):
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f); w.writerow(head); w.writerows(rows)
def ms(x): x = int(x); return x // 1000 if x > 1e14 else x
def last_day(rows): return dt.datetime.utcfromtimestamp(max(ms(r[0]) for r in rows) / 1000).date() if rows else dt.date(2024, 1, 1)
def days_between(d0, d1):
    d = d0
    while d <= d1: yield d; d += dt.timedelta(days=1)

def upd_klines(path, market, pair, pick):
    head, rows = read_gz(path)
    have = {ms(r[0]) for r in rows}; new = []
    for d in days_between(last_day(rows), TODAY - dt.timedelta(days=1)):
        b = get(f"{B}/{market}/daily/klines/{pair}/1h/{pair}-1h-{d}.zip")
        if b:
            for r in rows_of(b):
                if ms(r[0]) not in have: new.append(pick(r)); have.add(ms(r[0]))
    if new: write_gz(path, head, sorted(rows + new, key=lambda r: ms(r[0])))
    return len(new)

def job_fut(path):
    s = os.path.basename(path)[:-7]
    return "fut", s, upd_klines(path, "futures/um", f"{s}USDT", lambda r: [r[0], r[1], r[2], r[3], r[4], r[5], r[7], r[8]])
def job_spot(path):
    s = os.path.basename(path)[:-7]; base = s[4:] if s.startswith("1000") else s
    return "spot", s, upd_klines(path, "spot", f"{base}USDT", lambda r: [str(ms(r[0])), r[4], r[7]])
def job_fund(path):
    s = os.path.basename(path)[:-7]; head, rows = read_gz(path); have = {int(r[0]) for r in rows}; new = []
    d = last_day(rows).replace(day=1)
    while d < TODAY.replace(day=1):
        b = get(f"{B}/futures/um/monthly/fundingRate/{s}USDT/{s}USDT-fundingRate-{d:%Y-%m}.zip")
        if b:
            for r in rows_of(b):
                if int(r[0]) not in have: new.append([r[0], r[2]]); have.add(int(r[0]))
        d = (d + dt.timedelta(days=32)).replace(day=1)
    if new: write_gz(path, head, sorted(rows + new, key=lambda r: int(r[0])))
    return "fund", s, len(new)

def announcements():
    n = 0
    for cat in (48, 161, 49):
        p = f"ann/binance_{cat}.json"; old = json.load(open(p)) if os.path.exists(p) else []
        codes = {a["code"] for a in old}
        for page in range(1, 6):
            try:
                with urllib.request.urlopen(urllib.request.Request(
                        f"https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&catalogId={cat}&pageNo={page}&pageSize=50",
                        headers={**UA, "Accept": "application/json"}), timeout=30) as r:
                    arts = (json.load(r).get("data") or {}).get("catalogs", [{}])[0].get("articles", [])
            except Exception:
                break
            fresh = [{"title": a["title"], "code": a["code"], "releaseDate": a["releaseDate"]} for a in arts if a["code"] not in codes]
            old += fresh; codes |= {a["code"] for a in fresh}; n += len(fresh)
            if not fresh: break
            time.sleep(0.5)
        json.dump(sorted(old, key=lambda a: -a["releaseDate"]), open(p, "w"), ensure_ascii=False)
    return n

if __name__ == "__main__":
    jobs = [(job_fut, p) for p in glob.glob("data/*.csv.gz")] + [(job_spot, p) for p in glob.glob("spot/*.csv.gz")] + [(job_fund, p) for p in glob.glob("funding/*.csv.gz")]
    tot = {}
    with ThreadPoolExecutor(12) as ex:
        for kind, s, k in ex.map(lambda j: j[0](j[1]), jobs):
            tot[kind] = tot.get(kind, 0) + k
    tot["announcements"] = announcements()
    line = f"{dt.datetime.utcnow():%Y-%m-%d %H:%M} UTC | " + " | ".join(f"{k}: +{v}" for k, v in tot.items())
    print(line); open("UPDATES.log", "a").write(line + "\n")
