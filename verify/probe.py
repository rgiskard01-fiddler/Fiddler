import re, math, json, urllib.request, sys

def fetch(gid):
    for u in [f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt",
              f"https://www.gutenberg.org/files/{gid}/{gid}-0.txt"]:
        try:
            r=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"})
            return urllib.request.urlopen(r,timeout=45).read().decode("utf-8","replace")
        except Exception as e: last=e
    raise last

def strip(t):
    s=re.search(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*",t,re.S)
    e=re.search(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG",t)
    if s: t=t[s.end():]
    if e: t=t[:e.start()] if not s else t[:e.start()-0] if e.start()>0 else t
    # recompute end on the already-trimmed string
    e2=re.search(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG",t)
    if e2: t=t[:e2.start()]
    return t

def toks(t): return re.findall(r"[a-z']+", t.lower())

def heaps(tk, lo=800, hi=25000):
    """log-log fit of types vs tokens over the window"""
    seen=set(); xs=[]; ys=[]
    for i,w in enumerate(tk,1):
        seen.add(w)
        if i>=lo and i<=hi and i%50==0:
            xs.append(math.log(i)); ys.append(math.log(len(seen)))
        if i>hi: break
    if len(xs)<10: return None
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    num=sum((x-mx)*(y-my) for x,y in zip(xs,ys)); den=sum((x-mx)**2 for x in xs)
    return num/den

I_RE=re.compile(r"\b(i|my|me|mine|myself)\b")
def measure(name,year,kind,gid):
    raw=strip(fetch(gid)); tk=toks(raw)
    n=len(tk)
    b=heaps(tk)
    icount=sum(1 for w in tk if w in {"i","my","me","mine","myself"})
    # quotation PAIRS: count straight+curly double quotes, pairs = floor(count/2)
    q=raw.count('"')+raw.count('\u201c')+raw.count('\u201d')
    pairs=q//2
    return {"name":name,"year":year,"kind":kind,"gid":gid,"words":n,
            "types":len(set(tk)),"beta":round(b,4),
            "I":round(icount/n*1000,2),"voiced":round(pairs/n*1000,2)}

CAND=[("Pride+Prej",1813,"novel",1342),("Alice",1865,"novel",11),
      ("Origin",1859,"treatise",1228),("TaleTwoCities",1859,"novel",98),
      ("Prince",1532,"polemic",1232),("MobyDick",1851,"novel",2701),
      ("Iliad",-750,"epic",2199),("Odyssey",-720,"epic",1727),
      ("Federalist",1788,"apparatus",1404),("Meditations",180,"scripture",2680)]
out=[]
for c in CAND:
    try:
        m=measure(*c); out.append(m)
        print(f"{m['name']:15s} n={m['words']:>7,} beta={m['beta']:.4f} I={m['I']:>6.2f} voiced={m['voiced']:>6.2f}")
    except Exception as e:
        print(f"{c[0]:15s} FAILED: {type(e).__name__}", file=sys.stderr)
json.dump(out,open("new.json","w"),indent=1)
