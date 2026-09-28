# بيانات الساعة (سوق فوري، باينانس) لعملات أ5 من 2019-06 لين الحين — لاختبار الفريمات الصغيرة على 7 سنوات
import io, zipfile, csv, gzip, os, urllib.request, datetime as dt
from concurrent.futures import ThreadPoolExecutor
COINS=['1inch','aave','ada','algo','alpha','ant','bal','bat','bch','bnb','btc','comp','crv','cvc','dash','doge','dot','etc','eth','flow','ftt','gas','icp','knc','ldo','link','loom','lpt','ltc','mana','mkr','neo','omg','powr','qnt','ren','snt','snx','srm','sushi','trx','uma','uni','xem','xlm','xmr','xrp','xtz','xvg','yfi','zec','zrx']
today=dt.date.today(); months=[]
y,m=2019,6
while (y,m)<(today.year,today.month):
    months.append(f"{y}-{m:02d}"); m+=1
    if m>12: y,m=y+1,1
days=[(dt.date(today.year,today.month,1)+dt.timedelta(days=k)).isoformat() for k in range((today-dt.date(today.year,today.month,1)).days)]
def get(j):
    c,per,kind=j; p=f"{c.upper()}USDT"
    url=f"https://data.binance.vision/data/spot/{kind}/klines/{p}/1h/{p}-1h-{per}.zip"
    try:
        with urllib.request.urlopen(url,timeout=60) as r: b=r.read()
    except Exception: return j,[]
    rows=[]
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        for n in z.namelist():
            for r in csv.reader(io.TextIOWrapper(z.open(n))):
                if r and r[0][:1].isdigit():
                    t=int(r[0]); t=t//1000 if t>1e14 else t
                    rows.append((t,r[1],r[2],r[3],r[4],r[7]))
    return j,rows
jobs=[(c,p,"monthly") for c in COINS for p in months]+[(c,d,"daily") for c in COINS for d in days]
os.makedirs("h1",exist_ok=True); byc={}
with ThreadPoolExecutor(24) as ex:
    for (c,_,_),rows in ex.map(get,jobs): byc.setdefault(c,[]).extend(rows)
for c,rows in byc.items():
    if not rows: print(c,"none"); continue
    rows=sorted(set(rows))
    with gzip.open(f"h1/{c.upper()}.csv.gz","wt",newline="") as f:
        w=csv.writer(f); w.writerow(["t","o","h","l","c","qv"]); w.writerows(rows)
    print(c,len(rows),dt.datetime.utcfromtimestamp(rows[0][0]/1000).date(),dt.datetime.utcfromtimestamp(rows[-1][0]/1000).date())
