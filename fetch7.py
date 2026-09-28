# أسعار عقود باينانس (ساعة) للعملات اللي عندها فك قفل — من أول إدراجها
import io, zipfile, csv, gzip, os, json, re, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
UA={"User-Agent":"Mozilla/5.0"}
def get(u,t=60):
    with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t) as r: return r.read()
# 1) gecko id -> symbol
cg=None
for attempt in range(8):
    try:
        cg=json.loads(get("https://api.coingecko.com/api/v3/coins/list")); break
    except Exception as e:
        print("coingecko retry",attempt,e,flush=True); time.sleep(20*(attempt+1))
if cg is None:
    raise SystemExit("coingecko unavailable")
sym={c["id"]:c["symbol"].upper() for c in cg}
gk=[l.strip() for l in open("unlock_geckos.txt") if l.strip()]
# 2) all futures symbols on data.binance.vision
def s3list(prefix):
    out=[]; marker=""
    while True:
        u=f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix={prefix}&delimiter=/"+(f"&marker={marker}" if marker else "")
        x=get(u).decode()
        ps=re.findall(r"<Prefix>([^<]+)</Prefix>",x); ks=re.findall(r"<Key>([^<]+)</Key>",x)
        out+=ps[1:] if ps and ps[0]==prefix else ps; out+=ks
        if "<IsTruncated>true</IsTruncated>" not in x: break
        marker=(ps[-1] if ps else ks[-1])
    return out
fut={p.rstrip("/").split("/")[-1] for p in s3list("data/futures/um/monthly/klines/")}
m={}
for g in gk:
    s=sym.get(g)
    if not s: continue
    for cand in (s+"USDT","1000"+s+"USDT"):
        if cand in fut: m[g]=cand; break
json.dump(m,open("unlock_map.json","w"),indent=1); print("matched",len(m),"of",len(gk),flush=True)
# 3) download per symbol and write immediately
def dl(k):
    for attempt in range(3):
        try: b=get("https://data.binance.vision/"+k); break
        except Exception: time.sleep(2)
    else: return []
    rows=[]
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        for n in z.namelist():
            for r in csv.reader(io.TextIOWrapper(z.open(n))):
                if r and r[0][:1].isdigit(): rows.append((int(r[0]),r[1],r[2],r[3],r[4],r[7]))
    return rows
os.makedirs("ulp",exist_ok=True); cur=time.strftime("%Y-%m")
with ThreadPoolExecutor(24) as ex:
    for g,S in m.items():
        try:
            ks=[k for k in s3list(f"data/futures/um/monthly/klines/{S}/1h/") if k.endswith(".zip")]
            ks+=[k for k in s3list(f"data/futures/um/daily/klines/{S}/1h/") if k.endswith(".zip") and k.split("-1h-")[1][:7]>=cur]
        except Exception as e:
            print(S,"list fail",e,flush=True); continue
        rows=sorted(set(r for rr in ex.map(dl,ks) for r in rr))
        if not rows: continue
        with gzip.open(f"ulp/{S}.csv.gz","wt",newline="") as f:
            w=csv.writer(f); w.writerow(["t","o","h","l","c","qv"]); w.writerows(rows)
        print(S,len(ks),len(rows),flush=True)
