# سحب بيانات الساعة لعقود باينانس الآجلة (USDT) من الموقع الرسمي للبيانات العامة
import io, zipfile, datetime as dt, urllib.request, os, gzip, csv
from concurrent.futures import ThreadPoolExecutor
SYMS = """BTC ETH BNB SOL XRP DOGE ADA TRX AVAX LINK DOT MATIC POL LTC BCH NEAR UNI ATOM ETC FIL APT ARB OP SUI SEI TIA INJ STX IMX RNDR RENDER FET AGIX OCEAN GRT AAVE MKR LDO CRV SNX DYDX GMX PENDLE JUP PYTH JTO WIF 1000PEPE 1000SHIB 1000BONK 1000FLOKI ORDI 1000SATS WLD ENA ETHFI ONDO TAO TON NOT PEOPLE MEME BOME ENS ICP HBAR VET ALGO XLM XMR ZEC DASH EOS NEO QTUM KAVA RUNE THETA SAND MANA AXS GALA APE CHZ FTM S BLUR CFX KAS AR ALT STRK ZK ZRO W EIGEN TRUMP VIRTUAL AI16Z FARTCOIN PNUT NEIRO POPCAT GOAT MOODENG TURBO BRETT PENGU MOVE ME USUAL BERA IP KAITO LAYER JASMY IOTA XTZ EGLD FLOW MINA ROSE CELO 1INCH COMP YFI SUSHI LRC ZIL ICX ONE KSM WOO SSV GAS TRB BAND API3 MASK ACH HOOK MAGIC RDNT ID CYBER ARKM BIGTIME AEVO MANTA DYM PIXEL PORTAL AXL SAGA TNSR OM IO LISTA BANANA DOGS HMSTR CATI SCR GRASS DRIFT ACT THE HYPE SPX 1000CAT MEW BNX RSR SUN BAKE LUNA2 1000LUNC USTC GMT APT ENJ ATA C98 SXP ALICE DENT HOT CELR COTI KNC ANKR STORJ SKL BAT OGN RLC NKN ARPA IOTX CTSI LPT UMA BICO JOE HIGH EDU FXS CAKE XAI AI NFP ACE ORCA KMNO ZETA REZ BB TURBO""".split()
SYMS = list(dict.fromkeys(SYMS))
B = "https://data.binance.vision/data/futures/um"
def months():
    y, m = 2024, 1
    while (y, m) <= (2026, 8):
        yield f"{y}-{m:02d}"; m += 1
        if m == 13: y, m = y + 1, 1
def days():
    d = dt.date(2026, 9, 1)
    while d <= dt.date(2026, 9, 27):
        yield d.isoformat(); d += dt.timedelta(days=1)
def get(url):
    try:
        with urllib.request.urlopen(url, timeout=60) as r: return r.read()
    except Exception: return None
def parse(blob):
    out = []
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for n in z.namelist():
            for row in csv.reader(io.TextIOWrapper(z.open(n))):
                if not row or not row[0].isdigit(): continue
                out.append((int(row[0]), row[1], row[2], row[3], row[4], row[5], row[7], row[8]))
    return out
def one(sym):
    p = f"{sym}USDT"; rows = []
    for mo in months():
        b = get(f"{B}/monthly/klines/{p}/1h/{p}-1h-{mo}.zip")
        if b: rows += parse(b)
    for d in days():
        b = get(f"{B}/daily/klines/{p}/1h/{p}-1h-{d}.zip")
        if b: rows += parse(b)
    if not rows: return sym, 0
    rows = sorted(set(rows))
    os.makedirs("data", exist_ok=True)
    with gzip.open(f"data/{sym}.csv.gz", "wt", newline="") as f:
        w = csv.writer(f); w.writerow(["open_time", "open", "high", "low", "close", "volume", "quote_volume", "trades"]); w.writerows(rows)
    return sym, len(rows)
with ThreadPoolExecutor(12) as ex:
    for s, n in ex.map(one, SYMS): print(s, n, flush=True)
