# إعلانات باينانس (إدراج، شطب، علامات مراقبة) وإعلانات أبيت، مع وقتها الدقيق
import json, time, urllib.request, os
UA={"User-Agent":"Mozilla/5.0","Accept":"application/json"}
def get(url):
    for _ in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30) as r: return json.load(r)
        except Exception as e: err=e; time.sleep(2)
    print("FAIL",url,err); return None
os.makedirs("ann",exist_ok=True)
# Binance: 48 = new cryptocurrency listing, 161 = delisting, 49 = latest binance news (monitoring tags etc.)
for cat in (48,161,49,50):
    out=[]
    for page in range(1,60):
        js=get(f"https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&catalogId={cat}&pageNo={page}&pageSize=50")
        if not js: break
        cats=(js.get("data") or {}).get("catalogs") or []
        arts=cats[0].get("articles",[]) if cats else []
        if not arts: break
        out+= [{"title":a.get("title"),"code":a.get("code"),"releaseDate":a.get("releaseDate")} for a in arts]
        if arts[-1].get("releaseDate",0) < 1704067200000: break
        time.sleep(0.5)
    json.dump(out,open(f"ann/binance_{cat}.json","w"),ensure_ascii=False); print("binance",cat,len(out))
# Upbit announcements (trade category)
out=[]
for page in range(1,120):
    js=get(f"https://api-manager.upbit.com/api/v1/announcements?os=web&page={page}&per_page=50&category=trade")
    if not js: break
    lst=(js.get("data") or {}).get("notices") or (js.get("data") or {}).get("list") or []
    if not lst: break
    out+=lst
    last=lst[-1].get("listed_at") or lst[-1].get("created_at") or ""
    if last and last[:4] < "2024": break
    time.sleep(0.5)
json.dump(out,open("ann/upbit_trade.json","w"),ensure_ascii=False); print("upbit",len(out))
