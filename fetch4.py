# بيانات الدقيقة لعقود باينانس حول كل حدث (يوم قبل الحدث لين 7 أيام بعده)
import io, zipfile, csv, gzip, os, urllib.request, datetime as dt
from concurrent.futures import ThreadPoolExecutor
ev=list(csv.DictReader(open("events_min.csv")))
jobs=set()
for e in ev:
    d0=dt.date.fromisoformat(e["day"])
    for k in range(-1,8): jobs.add((e["ticker"], (d0+dt.timedelta(days=k)).isoformat()))
def get(j):
    tk,d=j; p=f"{tk}USDT"; url=f"https://data.binance.vision/data/futures/um/daily/klines/{p}/1m/{p}-1m-{d}.zip"
    try:
        with urllib.request.urlopen(url,timeout=60) as r: b=r.read()
    except Exception: return j,[]
    rows=[]
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        for n in z.namelist():
            for r in csv.reader(io.TextIOWrapper(z.open(n))):
                if r and r[0][:1].isdigit(): rows.append((int(r[0]),r[1],r[2],r[3],r[4]))
    return j,rows
os.makedirs("min1",exist_ok=True); byt={}
with ThreadPoolExecutor(16) as ex:
    for (tk,d),rows in ex.map(get,sorted(jobs)): byt.setdefault(tk,[]).extend(rows)
for tk,rows in byt.items():
    if not rows: continue
    with gzip.open(f"min1/{tk}.csv.gz","wt",newline="") as f:
        w=csv.writer(f); w.writerow(["t","o","h","l","c"]); w.writerows(sorted(set(rows)))
    print(tk,len(rows))
