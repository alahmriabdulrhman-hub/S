# تجربة مصادر مواعيد فك القفل (Token unlocks) — نحفظ اللي يشتغل
import json, os, urllib.request, time
os.makedirs("unlocks", exist_ok=True)
UA={"User-Agent":"Mozilla/5.0"}
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60) as r: return r.status, r.read()
    except Exception as e: return str(e)[:80], b""
probe={}
for u in ["https://api.llama.fi/emissions","https://defillama-datasets.llama.fi/emissionsProtocolsList",
          "https://defillama-datasets.llama.fi/emissionsIndex","https://api.llama.fi/emission/arbitrum",
          "https://defillama-datasets.llama.fi/emissions/arbitrum"]:
    st,b=get(u); probe[u]=(st,len(b),b[:300].decode("utf8","ignore")); print(u,st,len(b))
json.dump(probe,open("unlocks/probe.json","w"),indent=1,ensure_ascii=False)
# full pull from whichever list works
lst=None
for u in ["https://api.llama.fi/emissions","https://defillama-datasets.llama.fi/emissionsProtocolsList"]:
    st,b=get(u)
    if st==200 and b:
        lst=json.loads(b); open("unlocks/list.json","wb").write(b); print("list from",u,len(lst)); break
if lst is not None:
    names=[]
    for x in lst:
        n=x if isinstance(x,str) else (x.get("token") or x.get("name") or x.get("protocolId") or x.get("gecko_id"))
        if isinstance(x,dict): n=x.get("name") or n
        if n: names.append(str(n))
    ok=0
    for n in names:
        slug=n.lower().replace(" ","-")
        for u in (f"https://api.llama.fi/emission/{slug}",f"https://defillama-datasets.llama.fi/emissions/{slug}"):
            st,b=get(u)
            if st==200 and len(b)>100:
                open(f"unlocks/{slug}.json","wb").write(b); ok+=1; break
        time.sleep(0.2)
    print("protocol files:",ok,"of",len(names))
