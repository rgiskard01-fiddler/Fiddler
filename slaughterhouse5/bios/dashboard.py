"""Local dashboard for the Slaughterhouse5 biosphere — flashy interactive console.

Serves a live 3D-canvas view of the planet + an "enterprise" toolsuite over HTTP,
and can trigger PULSE runs / speciation. Dependency-free (pure Canvas 2D pseudo-3D,
no external CDNs) so it works offline.

  Run:   python -m bios.dashboard     (then open the printed URL)
  Win:   run-biosphere.bat
"""
from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from .kernel import BioSphere
from . import pulse
from .hermes import Hermes, NOVEL_POOL

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state")
PORT = int(os.environ.get("BIOS_PORT", "8753"))

_run_lock = threading.Lock()


def _load(name, default=None):
    p = os.path.join(STATE, name)
    if os.path.isfile(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return default
    return default


def _last_capsule(kind):
    cd = os.path.join(STATE, "capsules")
    if not os.path.isdir(cd):
        return None
    best = None
    for fn in os.listdir(cd):
        if not fn.endswith(".json"):
            continue
        try:
            c = json.load(open(os.path.join(cd, fn), encoding="utf-8"))
        except Exception:
            continue
        if c.get("kind") == kind:
            best = c
    return best


def run_pulse_bg(n: int, reset: bool = False):
    with _run_lock:
        pulse.run_pulse(BioSphere(), n=n, verbose=False, reset=reset)


def speciate_bg(ticks: int = 5):
    from . import speciate as _speciate
    with _run_lock:
        return _speciate.speciate(ticks=ticks)


def state_snapshot():
    ledger = _load("ledger.json", {})
    diffs = _load("differences.json", [])
    lg = _last_capsule("GOVERN")
    le = _last_capsule("EXECUTE")
    hm_path = os.path.join(STATE, "hermes.json")
    hm = {}
    if os.path.isfile(hm_path):
        try:
            h = json.load(open(hm_path, encoding="utf-8"))
            hm = {"skills": h.get("skills", []), "curiosity": h.get("curiosity", 0.5),
                  "retention": len(h.get("retention", [])), "last": h.get("retention", [])[-4:]}
        except Exception:
            pass
    return {
        "tick": ledger.get("ticks", 0),
        "genome": _load("learned.json", []),
        "population": _load("population.json", []),
        "differences_ticks": len(diffs),
        "learned_weight": _load("learned_weight.json", 0.6),
        "verdicts": [d.get("verdict") for d in diffs][-12:],
        "last_govern": lg.get("payload") if lg else None,
        "last_execute": le.get("payload") if le else None,
        "hermes": hm,
    }


HTML = r"""<!doctype html><meta charset=utf-8><title>Slaughterhouse5 — Biosphere Console</title>
<style>
  :root{--bg:#070a10;--panel:#0d1420;--edge:#1d2a3f;--fg:#d8e3ff;--mut:#7f97c4;
         --acc:#39e6c8;--warn:#ff7a7a;--gold:#ffd166;--blue:#5aa9ff;--teal:#39e6c8}
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;background:radial-gradient(1200px 800px at 70% -10%,#13233f,#070a10 60%);
            color:var(--fg);font:13px/1.45 ui-monospace,Menlo,Consolas,monospace;overflow:hidden}
  header{display:flex;align-items:center;gap:14px;padding:10px 16px;border-bottom:1px solid var(--edge);
         background:linear-gradient(90deg,#0b1320,#0d1420)}
  h1{font-size:15px;margin:0;color:var(--acc);letter-spacing:1px}
  .pill{background:#101a2c;border:1px solid var(--edge);border-radius:999px;padding:3px 10px;color:var(--mut)}
  .grow{flex:1}
  .toolbar button{background:#15243c;color:var(--fg);border:1px solid var(--edge);border-radius:8px;
                  padding:7px 12px;margin-left:6px;cursor:pointer}
  .toolbar button:hover{border-color:var(--acc);color:var(--acc)}
  main{display:grid;grid-template-columns:minmax(420px,1.1fr) 1.4fr;grid-template-rows:1fr 150px;
       gap:12px;padding:12px;height:calc(100% - 52px)}
  .card{background:var(--panel);border:1px solid var(--edge);border-radius:12px;padding:12px;overflow:auto;position:relative}
  .card h2{margin:0 0 8px;font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:1px}
  .col{display:grid;grid-template-rows:1fr 1fr;gap:12px}
  canvas{display:block;width:100%;height:100%;border-radius:10px;background:radial-gradient(400px 300px at 50% 40%,#0e1a30,#070a10)}
  .chip{display:inline-block;margin:3px;padding:4px 9px;border-radius:7px;background:#13233a;border:1px solid var(--edge)}
  .chip b{color:var(--acc)} .chip small{color:var(--mut)}
  table{width:100%;border-collapse:collapse} td,th{text-align:left;padding:3px 6px;border-bottom:1px solid #152034}
  .L1{color:var(--blue)} .L2{color:var(--teal)} .H{color:var(--gold)}
  .gauge{height:9px;border-radius:6px;background:linear-gradient(90deg,var(--warn),#ffe07a,var(--acc))}
  .gauge>i{display:block;height:100%;border-radius:6px;background:#070a10}
  .log{font-size:12px;color:var(--mut)} .log .hl{color:var(--acc)}
  #console{font-size:11px;color:#9fb4dd;white-space:pre-wrap;overflow:auto}
  .kpi{display:flex;gap:18px;margin-bottom:6px}
  .kpi div{font-size:11px;color:var(--mut)} .kpi b{color:var(--fg);font-size:15px}
</style>
<header>
  <h1>SLAUGHTERHOUSE5</h1><span class="pill" id=tick>tick 0</span>
  <span class="pill" id=weight>learned L4 weight 0.00</span>
  <span class="pill" id=hermes>HERMES cur 0.50</span>
  <span class="grow"></span>
  <span class="toolbar">
    <button onclick="run(10,false)">Run 10</button>
    <button onclick="run(10,true)">Reset &amp; Run</button>
    <button onclick="speciate(5)">Speciate</button>
  </span>
</header>
<main>
  <div class="card"><h2>Biosphere — 3D planet (L1→L4 descent)</h2><canvas id=planet></canvas></div>
  <div class="col">
    <div class="card"><h2>Genome explorer &amp; L4 weight</h2>
      <div class="kpi"><div>tick<br><b id=k2>0</b></div><div>diffs logged<br><b id=d2>0</b></div><div>population<br><b id=p2>0</b></div></div>
      <div class="gauge"><i id=gfill></i></div>
      <div id=genome style="margin-top:8px"></div>
    </div>
    <div class="card"><h2>Population matrix</h2><div id=pop></div></div>
  </div>
  <div class="card" style="grid-column:1"><h2>Governance / differences log</h2><div id=gov class=log></div></div>
  <div class="card"><h2>Hermes (special agent) &amp; L4 inspector</h2>
    <div id=hermesp></div><div id=l4 style="margin-top:8px" class=log></div>
  </div>
</main>
<div class="card" style="position:fixed;left:12px;right:12px;bottom:10px;height:140px"><h2>Console</h2><div id=console></div></div>
<script>
const cv=document.getElementById('planet'), ctx=cv.getContext('2d');
function resize(){cv.width=cv.clientWidth*devicePixelRatio;cv.height=cv.clientHeight*devicePixelRatio;}
resize(); addEventListener('resize',resize);
let angle=0;
function rot(x,y,z){const cY=Math.cos(angle),sY=Math.sin(angle);
  let x1=x*cY-z*sY, z1=x*sY+z*cY; const cX=Math.cos(0.45),sX=Math.sin(0.45);
  let y1=y*cX-z1*sX, z2=y*sX+z1*cX; const f=320/(z2+320);
  return [cv.width/2+x1*f, cv.height/2+y1*f, z2, f];}
function sphere(r,n){const pts=[];const phi=Math.PI*(3-Math.sqrt(5));
  for(let i=0;i<n;i++){const y=1-(i/(n-1))*2;const rxy=Math.sqrt(1-y*y);const th=phi*i;
    pts.push([Math.cos(th)*rxy*r, y*r, Math.sin(th)*rxy*r]);}return pts;}
const shells={L4:24,L3:78,L2:130,L1:182,H:156};
let NODES=[]; let lastTick=-1;
function draw(S){
  angle+=0.004; ctx.clearRect(0,0,cv.width,cv.height);
  // planet shells
  for(const [k,r] of Object.entries(shells)){
    ctx.strokeStyle = k==='L4'?'rgba(255,209,102,.25)':k==='H'?'rgba(255,209,102,.18)':k==='L2'?'rgba(57,230,200,.14)':'rgba(90,169,255,.14)';
    for(const p of sphere(r, k==='L4'?40:90)){const q=rot(p[0],p[1],p[2]);ctx.fillRect(q[0],q[1],1,1);}
  }
  // center cortex
  const c=rot(0,0,0); ctx.fillStyle='#ffd166'; ctx.beginPath();ctx.arc(c[0],c[1],5*c[3],0,7);ctx.fill();
  // nodes from population + hermes
  NODES=[]; const pop=(S.population||[]);
  pop.forEach((m,i)=>{const sh=shells[m.plane]||shells.L1; const a=i*0.9; NODES.push({x:Math.cos(a)*sh,y:Math.sin(a*1.3)*sh,z:Math.sin(a)*sh,plane:m.plane});});
  if(S.hermes&&S.hermes.skills){NODES.push({x:Math.cos(1.2)*shells.H,y:Math.sin(1.2)*shells.H,z:Math.cos(1.2)*shells.H,plane:'H'});}
  NODES.forEach(n=>{const q=rot(n.x,n.y,n.z);const col=n.plane==='L1'?'#5aa9ff':n.plane==='L2'?'#39e6c8':n.plane==='H'?'#ffd166':'#fff';
    ctx.strokeStyle='rgba(120,160,220,.12)';ctx.beginPath();ctx.moveTo(c[0],c[1]);ctx.lineTo(q[0],q[1]);ctx.stroke();
    ctx.fillStyle=col;ctx.beginPath();ctx.arc(q[0],q[1],4*q[3],0,7);ctx.fill();});
  if(S.tick!==lastTick){lastTick=S.tick; for(let i=0;i<24;i++){const a=Math.random()*7,p=sphere(60+Math.random()*120,1)[0];const q=rot(p[0],p[1],p[2]);ctx.fillStyle='rgba(57,230,200,.5)';ctx.fillRect(q[0],q[1],2,2);} }
}
function render(S){
  document.getElementById('tick').textContent='tick '+S.tick;
  document.getElementById('k2').textContent=S.tick;
  document.getElementById('d2').textContent=S.differences_ticks;
  document.getElementById('p2').textContent=(S.population||[]).length;
  const lw=S.learned_weight||0;
  document.getElementById('weight').textContent='learned L4 weight '+lw.toFixed(3);
  document.getElementById('gfill').style.width=(50+lw*50)+'%';
  document.getElementById('hermes').textContent='HERMES cur '+(S.hermes.curiosity||0).toFixed(2);
  document.getElementById('genome').innerHTML=(S.genome||[]).slice(-14).map(g=>
    `<span class=chip><b>${g.toward||'?'}</b> <small>w:${(g.weight||0).toFixed(2)}</small></span>`).join('');
  document.getElementById('pop').innerHTML='<table><tr><th>name</th><th>plane</th><th>fit</th><th>gen</th></tr>'+
    (S.population||[]).map(p=>`<tr><td>${p.name}</td><td class=${p.plane}>${p.plane}</td><td>${p.fitness}</td><td>${p.gen}</td></tr>`).join('')+'</table>';
  const lg=S.last_govern;
  document.getElementById('gov').innerHTML = lg?
    `<span class=hl>verdict ${lg.verdict}</span> · distinct ${JSON.stringify(lg.distinct)} · taught ${JSON.stringify(lg.taught)}<br>pop ${JSON.stringify(lg.population)}`:
    'awaiting governance…';
  const h=S.hermes||{}; 
  document.getElementById('hermesp').innerHTML=`<span class=chip><b>skills</b> <small>${(h.skills||[]).join(', ')}</small></span>
     <span class=chip><b>curiosity</b> <small>${(h.curiosity||0).toFixed(2)}</small></span>
     <span class=chip><b>retention</b> <small>${h.retention||0}</small></span>`+
     (h.last?`<div class=log style="margin-top:6px">recall: ${JSON.stringify(h.last)}</div>`:'');
  const le=S.last_execute;
  document.getElementById('l4').innerHTML = le?`<span class=hl>EXECUTE ${le.status}</span>`+
     (le.operants?` · ops ${le.operants.join(',')}`:'')+(le.reason?` · ${le.reason}`:''):'L4 idle';
  document.getElementById('console').textContent=JSON.stringify({tick:S.tick,verdicts:S.verdicts},null,0);
}
function tick(){fetch('/state').then(r=>r.json()).then(S=>{draw(S);render(S);}).catch(()=>{});}
function run(n,reset){fetch('/run?n='+n+'&reset='+reset).then(()=>setTimeout(tick,400));}
function speciate(t){fetch('/speciate?ticks='+t).then(r=>r.json()).then(j=>alert('Speciation done: '+JSON.stringify(j)));}
setInterval(tick,1500); tick();
</script>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        import urllib.parse as up
        if self.path.startswith("/state"):
            self._send(200, json.dumps(state_snapshot()))
        elif self.path.startswith("/run"):
            q = up.parse_qs(up.urlparse(self.path).query)
            n = int(q.get("n", ["10"])[0]); reset = q.get("reset", ["false"])[0] == "true"
            threading.Thread(target=run_pulse_bg, args=(n, reset), daemon=True).start()
            self._send(200, json.dumps({"ok": True, "n": n, "reset": reset}))
        elif self.path.startswith("/speciate"):
            q = up.parse_qs(up.urlparse(self.path).query)
            t = int(q.get("ticks", ["5"])[0])
            thr = threading.Thread(target=speciate_bg, args=(t,), daemon=True)
            thr.start(); thr.join(timeout=60)
            self._send(200, json.dumps(speciate_bg(t)))
        elif self.path.startswith("/hermes"):
            hm = Hermes(STATE)
            self._send(200, json.dumps({"skills": hm.skills, "curiosity": hm.curiosity,
                                        "retention": len(hm.retention), "last": hm.recall(4)}))
        elif self.path in ("/", "/index.html"):
            self._send(200, HTML, "text/html")
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def log_message(self, *a):
        pass


def main():
    import webbrowser
    srv = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Slaughterhouse5 console -> http://127.0.0.1:{PORT}/")
    print("  3D planet + enterprise toolsuite. Triggers PULSE / speciation in-process.")
    try:
        webbrowser.open(f"http://127.0.0.1:{PORT}/")
    except Exception:
        pass
    srv.serve_forever()


if __name__ == "__main__":
    main()
