import re, urllib.request
src=open("probe.py").read().split("CAND=")[0]; ns={}; exec(src,ns)
fetch,strip,toks=ns["fetch"],ns["strip"],ns["toks"]

HIS={"JaneEyre":(1260,9.73),"Wuthering":(768,9.66),"Walden":(205,1.30),"AgnesGrey":(767,6.68)}
RULES={
 "all_quote_chars//2": lambda r:(r.count('"')+r.count('\u201c')+r.count('\u201d'))//2,
 "opening_curly_only": lambda r: r.count('\u201c'),
 "straight_only//2":   lambda r: r.count('"')//2,
 "regex_paired":       lambda r: len(re.findall(r'["\u201c][^"\u201c\u201d]*["\u201d]',r)),
 "all_chars//4":       lambda r:(r.count('"')+r.count('\u201c')+r.count('\u201d'))//4,
 "lines_with_quote":   lambda r: sum(1 for L in r.split("\n") if '"' in L or '\u201c' in L),
 "paragraphs_quoted":  lambda r: sum(1 for p in re.split(r"\n\s*\n",r) if '"' in p or '\u201c' in p),
}
print(f"{'RULE':22s} " + " ".join(f"{k:>11s}" for k in HIS) + "   VERDICT")
cache={}
for nm,(gid,_) in HIS.items():
    raw=strip(fetch(gid)); cache[nm]=(raw,len(toks(raw)))
for rn,fn in RULES.items():
    row=[]; ok=True
    for nm,(gid,his) in HIS.items():
        raw,n=cache[nm]; got=fn(raw)/n*1000
        row.append(got); 
        if abs(got-his)>0.35: ok=False
    print(f"{rn:22s} " + " ".join(f"{v:11.2f}" for v in row) + ("   ** REPRODUCES **" if ok else ""))
print(f"{'HIS PUBLISHED':22s} " + " ".join(f"{HIS[k][1]:11.2f}" for k in HIS))
