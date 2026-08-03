"""Local dashboard for the Slaughterhouse5 biosphere — interactive WebGL console.

Real 3D via bundled Three.js (inlined into the HTML so the page is one
self-contained file; works offline, no CDN). An "enterprise" toolsuite with a
LIVE SSE stream (Tier 1: ticks push to the browser the instant they happen) and
clickable agent dossiers (Tier 3: per-agent history). Standard library only.

Refinement: a HONEYCOMB of glowing hexagonal blanks (each = a node, metric
label inside). Clicking a hex opens a "house style" floating window with five
sub-windows:
  w1 product description · w2 contributors/ideas posited · w3 1d fold of 2d/3d
  (shadow + shadow overlay) · w4 2d instrument running · w5 interactive 3d.

  Run:   python -m bios.dashboard     (then open the printed URL)
  Win:   run-biosphere.bat
"""
from __future__ import annotations

import json
import os
import queue
import socketserver
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .kernel import BioSphere
from . import pulse
from .hermes import Hermes, NOVEL_POOL

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state")
STATIC = os.path.join(HERE, "static")
PORT = int(os.environ.get("BIOS_PORT", "8753"))

_run_lock = threading.Lock()
# SSE broadcast queue — run threads push ticks, the /stream handler drains them
_BROADCAST = queue.Queue(maxsize=200)
_TRANS = {"playing": False, "speed": 3, "last_run": 0}

try:
    with open(os.path.join(STATIC, "three.min.js"), "r", encoding="utf-8") as _f:
        THREE_JS = _f.read()
except Exception:
    THREE_JS = ""  # degraded: 3D canvas will show a clear error in-console


def _load(name, default=None):
    p = os.path.join(STATE, name)
    if os.path.isfile(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return default
    return default


def _capsules(kind=None):
    cd = os.path.join(STATE, "capsules")
    out = []
    if not os.path.isdir(cd):
        return out
    for fn in sorted(os.listdir(cd)):
        if not fn.endswith(".json"):
            continue
        try:
            c = json.load(open(os.path.join(cd, fn), encoding="utf-8"))
        except Exception:
            continue
        if kind is None or c.get("kind") == kind:
            out.append(c)
    return out


def _broadcast(bio, snap):
    try:
        _BROADCAST.put_nowait(snap)
    except Exception:
        pass


def run_pulse_bg(n: int, reset: bool = False):
    with _run_lock:
        _TRANS["playing"] = True
        pulse.run_pulse(BioSphere(), n=n, verbose=False, reset=reset, on_tick=_broadcast)
        _TRANS["playing"] = False
        _TRANS["last_run"] = time.time()


def speciate_bg(ticks: int = 5):
    from . import speciate as _speciate
    with _run_lock:
        return _speciate.speciate(ticks=ticks)


def state_snapshot():
    ledger = _load("ledger.json", {})
    diffs = _load("differences.json", [])
    govern = [c for c in _capsules("GOVERN")]
    execute = [c for c in _capsules("EXECUTE")]
    hm_path = os.path.join(STATE, "hermes.json")
    hm = {}
    if os.path.isfile(hm_path):
        try:
            h = json.load(open(hm_path, encoding="utf-8"))
            hm = {"skills": h.get("skills", []), "curiosity": h.get("curiosity", 0.5),
                  "retention": len(h.get("retention", [])), "last": h.get("retention", [])[-5:]}
        except Exception:
            pass
    zones_caps = [c for c in _capsules("govern_zones")]
    weight_hist = _load("weight_history.json", [])
    return {
        "tick": ledger.get("ticks", 0),
        "genome": _load("learned.json", []),
        "population": _load("population.json", []),
        "differences_ticks": len(diffs),
        "learned_weight": _load("learned_weight.json", 0.6),
        "weight_history": weight_hist[-60:],
        "verdicts": [(d.get("verdict") or "?") for d in diffs][-20:],
        "govern": [c.get("payload") for c in govern][-6:],
        "execute": [c.get("payload") for c in execute][-6:],
        "zones": (zones_caps[-1].get("payload") if zones_caps else None),
        "capsule_log": [(c.get("kind"), c.get("sender")) for c in _capsules()][-30:],
        "hermes": hm,
        "playing": _TRANS["playing"],
        "speed": _TRANS["speed"],
    }


def agent_dossier(name):
    hist = _load("agent_history.json", {})
    return hist.get(name)


HTML = r"""<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Slaughterhouse5 — Biosphere Console</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<style>
  :root{--bg:#05070c;--panel:#0c1320;--edge:#1c2940;--fg:#e3ecff;--mut:#8298c6;
        --acc:#3af0cf;--warn:#ff6b6b;--gold:#ffd166;--blue:#62a9ff;--teal:#3af0cf}
  *{box-sizing:border-box}
  html,body{margin:0;min-height:100%;background:var(--bg);color:var(--fg);
            font:13px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
  #app{display:grid;grid-template-rows:48px 1fr 30px;height:100vh;min-height:100vh}
  header{display:flex;align-items:center;gap:12px;padding:0 16px;border-bottom:1px solid var(--edge);
         background:linear-gradient(90deg,#0a1120,#0c1320)}
  h1{font-size:15px;margin:0;color:var(--acc);letter-spacing:2px}
  .pill{background:#0f1a2c;border:1px solid var(--edge);border-radius:999px;padding:3px 10px;color:var(--mut);font-size:12px}
  .grow{flex:1}
  .transport button{background:#13233a;color:var(--fg);border:1px solid var(--edge);border-radius:7px;padding:6px 11px;margin-left:5px;cursor:pointer}
  .transport button:hover{border-color:var(--acc);color:var(--acc)}
  main{position:relative;overflow:hidden;padding:0}
  .panel{background:var(--panel);border:1px solid var(--edge);border-radius:12px;padding:10px;overflow:hidden;position:relative;display:flex;flex-direction:column}
  .panel h2{margin:0 0 8px;font-size:10px;color:var(--mut);text-transform:uppercase;letter-spacing:1.5px}
  .tabs{display:flex;gap:6px;margin-bottom:8px;flex-wrap:wrap}
  .tabs button{background:#0f1a2c;border:1px solid var(--edge);color:var(--mut);border-radius:7px;padding:5px 10px;cursor:pointer;font-size:12px}
  .tabs button.on{color:var(--acc);border-color:var(--acc)}
  .tabbody{flex:1;overflow:auto}
  table{width:100%;border-collapse:collapse} td,th{text-align:left;padding:4px 7px;border-bottom:1px solid #14202f;font-size:12px}
  .L1{color:var(--blue)} .L2{color:var(--teal)} .H{color:var(--gold)} .L4{color:var(--gold)}
  .chip{display:inline-block;margin:3px;padding:4px 9px;border-radius:7px;background:#12233a;border:1px solid var(--edge);font-size:12px}
  .chip b{color:var(--acc)} .chip small{color:var(--mut)}
  .kpis{display:flex;gap:16px;margin-bottom:8px}
  .kpis div{font-size:11px;color:var(--mut)} .kpis b{color:var(--fg);font-size:16px}
  #chart{width:100%;height:120px;background:#070d18;border:1px solid var(--edge);border-radius:8px}
  .log{font-size:12px;color:var(--mut);white-space:pre-wrap}
  .log .hl{color:var(--acc)} .log .w{color:var(--gold)}
  #status{font-size:11px;color:var(--mut);padding:0 14px;border-top:1px solid var(--edge);display:flex;align-items:center;gap:14px}
  .dot{width:8px;height:8px;border-radius:50%;background:var(--acc);display:inline-block;box-shadow:0 0 8px var(--acc)}
  .dot.off{background:#3a4a63;box-shadow:none}
  .dot.live{animation:pulse 1s infinite} @keyframes pulse{50%{opacity:.35}}
  .mini{display:inline-block;margin:2px 3px;padding:2px 6px;border-radius:5px;background:#12233a;border:1px solid var(--edge);font-size:11px}
  .mini.sel{border-color:var(--gold);color:var(--gold)} .mini.taught{color:var(--warn)}
  /* honeycomb */
  #hexwrap{flex:1;overflow:auto;background:radial-gradient(600px 400px at 50% 35%,#0a1424,#05070c);border-radius:10px}
  #hex{width:100%;display:block}
  .hexpoly{fill:#0e1a30;stroke:#3af0cf;stroke-width:2;cursor:grab;transition:fill .15s,stroke .15s}
  .hexpoly:hover{fill:#16263e;stroke-width:3}
  @keyframes hexpulse{0%,100%{filter:drop-shadow(0 0 2px var(--neon));stroke-width:2}
    50%{filter:drop-shadow(0 0 9px var(--neon)) drop-shadow(0 0 16px var(--neon));stroke-width:3.4}}
  .hextx{fill:#e3ecff;font:bold 11px ui-monospace,monospace;text-anchor:middle;pointer-events:none}
  .hextx.m{fill:#8298c6;font:10px ui-monospace,monospace}
  /* house-style windows */
  #houses{position:fixed;inset:0;pointer-events:none;z-index:50}
  .house{position:fixed;width:540px;max-width:94vw;background:linear-gradient(180deg,#0c1320,#0a0f1a);
         border:1px solid var(--edge);border-radius:10px;box-shadow:0 18px 55px rgba(0,0,0,.65);
         pointer-events:auto;display:flex;flex-direction:column;overflow:hidden}
  .house.max{width:92vw;height:82vh}
  .house-bar{display:flex;align-items:center;justify-content:space-between;padding:7px 10px;
             background:linear-gradient(90deg,#13233a,#1c2f4c);border-bottom:1px solid var(--edge);cursor:move}
  .house-title{font-size:13px;color:var(--acc);letter-spacing:1px}
  .house-btns .hb{display:inline-block;width:18px;text-align:center;margin-left:5px;color:var(--mut);cursor:pointer;user-select:none}
  .house-btns .hb.close:hover{color:var(--warn)} .house-btns .hb.max:hover,.house-btns .hb.min:hover{color:var(--acc)}
  .house-body{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:10px}
  .w{border:1px solid var(--edge);border-radius:8px;padding:8px;background:#0a121f;min-height:96px;display:flex;flex-direction:column}
  .w1{grid-column:1/2}.w2{grid-column:2/3}.w3{grid-column:1/2}.w4{grid-column:2/3}.w5{grid-column:1/3}
  .wlab{font-size:10px;color:var(--mut);text-transform:uppercase;letter-spacing:1.2px;margin-bottom:6px}
  .wcontent{font-size:12px;color:var(--fg);line-height:1.5;overflow:auto}
  .wcontent .desc{color:var(--fg)} .kv{font-size:12px;color:var(--mut);margin:3px 0} .kv b{color:var(--fg)}
  .w3 canvas,.w4 canvas,.w5 canvas{width:100%;flex:1;min-height:120px;display:block;background:#070d18;border-radius:6px;margin-top:4px}
  .w5 canvas{min-height:180px}
  /* full-window honeycomb */
  #hexwrap{position:absolute;inset:0;border-radius:0}
  #hex{width:100%;height:100%}
  .hexpoly{cursor:grab}
  .hexpoly.drag{cursor:grabbing}
  .hexpoly.locked{stroke:#ffd166;fill:#3a2f12}
  /* slide-in toolsuite */
  #toolbtn{position:absolute;top:12px;right:12px;z-index:20;background:#13233a;color:var(--acc);
           border:1px solid var(--acc);border-radius:8px;padding:7px 14px;cursor:pointer;font:12px ui-monospace,monospace}
  #toolbtn:hover{background:#1c2f4c}
  #suite{position:absolute;top:0;right:0;height:100%;width:46%;min-width:340px;max-width:680px;
         background:rgba(10,16,26,.96);border-left:1px solid var(--edge);box-shadow:-12px 0 40px rgba(0,0,0,.5);
         transform:translateX(102%);transition:transform .25s ease;z-index:19;display:flex;flex-direction:column;padding:10px;overflow:hidden}
  #suite.open{transform:translateX(0)}
  #suite .close{position:absolute;top:8px;right:10px;color:var(--mut);cursor:pointer}
  #suite .close:hover{color:var(--warn)}
  #hint{position:absolute;bottom:10px;left:12px;z-index:18;color:var(--mut);font-size:11px;
        background:rgba(10,16,26,.7);border:1px solid var(--edge);border-radius:6px;padding:4px 8px}

</style></head><body><div id=app>
<header>
  <h1>SLAUGHTERHOUSE5</h1><span class=pill id=tk>tick 0</span>
  <span class=pill id=wgt>L4 weight 0.00</span><span class=pill id=hm>HERMES 0.50</span>
  <span class=grow></span>
  <span class=transport>
    <button onclick=togglePlay()>▶ Run</button>
    <button onclick=stepRun(1)>Step</button>
    <button onclick=resetRun()>Reset</button>
    <button onclick=speciate(5)>⚡ Speciate</button>
    <label style="color:var(--mut)">speed <input id=spd type=range min=1 max=10 value=3 style="vertical-align:middle" oninput="setSpeed(this.value)"></label>
  </span>
</header>
<main>
  <div class=panel style="position:absolute;inset:0;border-radius:0"><h2>Node Honeycomb — drag the hexes · CORTEX is locked at center · click a hex to open its house window</h2>
    <div id=hexwrap><svg id=hex xmlns="http://www.w3.org/2000/svg"></svg></div>
  </div>
  <div id=toolbtn onclick="document.getElementById('suite').classList.toggle('open')">☰ Toolsuite</div>
  <div id=hint>drag hexes to arrange · CORTEX locked center · click hex → house window (w1–w5) · <span style=cursor:pointer;color:var(--acc) onclick=fitHex()>[fit]</span></div>
  <div id=suite>
    <span class=close onclick="document.getElementById('suite').classList.remove('open')">✕</span>
    <div class=tabs>
      <button class=on onclick=tab('genome',this)>Genome + L4</button>
      <button onclick=tab('pop',this)>Population</button>
      <button onclick=tab('gov',this)>Governance</button>
      <button onclick=tab('herm',this)>Hermes</button>
      <button onclick=tab('zones',this)>Zoned Gov</button>
      <button onclick=tab('log',this)>Capsule log</button>
    </div>
    <div class=tabbody id=tab-genome>
      <div class=kpis><div>tick<br><b id=k2>0</b></div><div>diffs<br><b id=d2>0</b></div><div>population<br><b id=p2>0</b></div><div>verdicts<br><b id=v2>0</b></div></div>
      <canvas id=chart></canvas>
      <div id=genome style="margin-top:8px"></div>
    </div>
    <div class=tabbody id=tab-pop style="display:none"><div id=pop></div></div>
    <div class=tabbody id=tab-gov style="display:none"><div id=gov class=log></div></div>
    <div class=tabbody id=tab-herm style="display:none"><div id=herm></div></div>
    <div class=tabbody id=tab-zones style="display:none"><div id=zones class=log></div></div>
    <div class=tabbody id=tab-log style="display:none"><div id=clog class=log></div></div>
  </div>
</main>
<div id=status><span><span class="dot off" id=playdot></span> <span id=live>offline</span></span><span id=stmsg></span><span class=grow></span><span>click a hex → house window · w5 = interactive 3d</span></div>
<div id=houses></div>
</div>

<script>/*__THREE__*/</script>
<script>
// ---------- node model ----------
function planeColor(p){
  // natural per-function neon: L1 democratic=blue, L2 stewardship=cyan,
  // H hermes=gold, L4 cortex=violet (sovereign), z governance=pink (the wall), core=green (life)
  return p==='L1'?'#4da6ff':p==='L2'?'#3af0cf':p==='H'?'#ffd166':p==='L4'?'#c77dff':p==='z'?'#ff5d8f':p==='core'?'#5dff9b':'#4da6ff';
}
function planeDesc(p){
  return ({
    L1:'Democratic sub-agent (z2\\l1). Proposes operants and votes in the 2/3 arbitration. Fitness = alignment with the winning verdict.',
    L2:'Stewardship sub-sub agent (z3\\l2). Bound by guardian rules: preserve genome continuity, no-harm (never delete state).',
    H:'Special modular citizen (plane H). Skills + retention + curiosity. The external agent, admitted to the sovereign scope.',
    L4:'Hegemonic sovereign (z1\\l0, S). Deep-operand resolver and seal authority. A veto is a wall.',
    z:'Zoned protocol: z1 sovereign / z2 democratic / z3 stewardship, sealed <->, enforced at the kernel emit.',
    core:'The whole biosphere — L1..L4 descending, closed by the i4 identity root. w5 shows the live 3D planet.'
  })[p] || 'Biosphere organ.';
}
function buildNodes(S){
  const nodes=[];
  (S.population||[]).forEach(p=>{
    const plane=p.plane; const kind=plane==='L1'?'agent':plane==='L2'?'subagent':plane==='H'?'hermes':'other';
    nodes.push({name:p.name, plane, kind, color:planeColor(plane), desc:planeDesc(plane),
      metric:'fit '+(p.fitness!=null?p.fitness:'?'), proposed:p.proposed, _fit:parseFloat(p.fitness)||0.5});
  });
  if(S.hermes) nodes.push({name:'HERMES', plane:'H', kind:'hermes', color:planeColor('H'), desc:planeDesc('H'),
      metric:'cur '+(S.hermes.curiosity||0).toFixed(2), _fit:S.hermes.curiosity||0.6});
  nodes.push({name:'CORTEX', plane:'L4', kind:'cortex', color:planeColor('L4'), desc:planeDesc('L4'),
      metric:'L4 resolver', _fit:0.9});
  nodes.push({name:'GOVERNANCE', plane:'z', kind:'gov', color:planeColor('z'), desc:planeDesc('z'),
      metric:'sealed', _fit:0.7});
  nodes.push({name:'BIOSPHERE', plane:'core', kind:'core', color:planeColor('core'), desc:planeDesc('core'),
      metric:'planet', _fit:0.6});
  return nodes;
}
// ---------- honeycomb ----------
const hexPos={};   // name -> {x,y}
const polyById={}; // name -> polygon element (for live drag)
function hexPts(cx,cy,R){let s='';for(let k=0;k<6;k++){const a=Math.PI/180*(60*k);s+=(cx+R*Math.cos(a)).toFixed(1)+','+(cy+R*Math.sin(a)).toFixed(1)+' ';}return s.trim();}
// axial hex spiral -> nearest neighbours touch (true honeycomb lock)
function honeycombSpiral(n){
  const cells=[]; let q=0,r=0;
  cells.push([q,r]);
  const dirs=[[1,0],[0,1],[-1,1],[-1,0],[0,-1],[1,-1]];
  let d=0, steps=1;
  while(cells.length<n){
    for(let s=0;s<2;s++){ // repeat each step length twice (hex spiral)
      for(let i=0;i<steps;i++){ if(cells.length>=n) break; q+=dirs[d][0]; r+=dirs[d][1]; cells.push([q,r]); }
      d=(d+1)%6;
    }
    steps++;
  }
  return cells;
}
function drawHex(nodes){
  const svg=document.getElementById('hex'); if(!svg)return;
  const R=46, W=svg.clientWidth||900, H=svg.clientHeight||640;
  svg.setAttribute('viewBox','0 0 '+W+' '+H);
  while(svg.firstChild) svg.removeChild(svg.firstChild);
  const cx=W/2, cy=H/2;
  if(!Object.keys(hexPos).length){
    const cells=honeycombSpiral(nodes.length);
    nodes.forEach((n,i)=>{
      if(n.name==='CORTEX'){hexPos[n.name]={x:cx,y:cy,locked:true};}
      else{const [q,r]=cells[i]; const dx=R*1.5, dy=R*Math.sqrt(3);
        hexPos[n.name]={x:cx+q*dx, y:cy+r*dy + q*dy/2};}
    });
  }
  nodes.forEach(n=>{
    let p=hexPos[n.name]; if(!p){p={x:cx,y:cy}; hexPos[n.name]=p;}
    if(p.locked){p.x=cx; p.y=cy;}
    if(n.name==='CORTEX') n.metric='★ center';
    const poly=document.createElementNS('http://www.w3.org/2000/svg','polygon');
    poly.setAttribute('points',hexPts(p.x,p.y,R));
    poly.setAttribute('class','hexpoly'+(p.locked?' locked':''));
    poly.style.stroke=n.color;
    poly.style.setProperty('--neon', n.color);
    poly.style.animation='hexpulse 2.4s ease-in-out infinite';
    poly.addEventListener('mousedown',e=>startHexDrag(e,n,p));
    poly.addEventListener('click',e=>{if(!p._moved)openHouse(n);});
    svg.appendChild(poly);
    const t1=document.createElementNS('http://www.w3.org/2000/svg','text');
    t1.setAttribute('x',p.x); t1.setAttribute('y',p.y-2); t1.setAttribute('class','hextx'); t1.textContent=n.name;
    svg.appendChild(t1);
    const t2=document.createElementNS('http://www.w3.org/2000/svg','text');
    t2.setAttribute('x',p.x); t2.setAttribute('y',p.y+12); t2.setAttribute('class','hextx m'); t2.textContent=n.metric||'';
    svg.appendChild(t2);
    polyById[n.name]=poly; p._t1=t1; p._t2=t2;
  });
}
function fitHex(){ for(const k in hexPos) delete hexPos[k]; drawHex(buildNodes(lastStatic)); }
function startHexDrag(e,n,p){
  if(p.locked) return;
  e.preventDefault(); e.stopPropagation();
  const svg=document.getElementById('hex');
  const r=svg.getBoundingClientRect();
  const sx=r.width/svg.viewBox.baseVal.width, sy=r.height/svg.viewBox.baseVal.height;
  const ox=p.x - (e.clientX-r.left)/sx, oy=p.y - (e.clientY-r.top)/sy;
  p._moved=false;
  const el=polyById[n.name];
  if(el){el.setAttribute('class','hexpoly drag');}
  function move(ev){
    p.x=ox+(ev.clientX-r.left)/sx; p.y=oy+(ev.clientY-r.top)/sy; p._moved=true;
    if(el){el.setAttribute('points',hexPts(p.x,p.y,46));}
    if(p._t1) p._t1.setAttribute('x',p.x); if(p._t1) p._t1.setAttribute('y',p.y-2);
    if(p._t2) p._t2.setAttribute('x',p.x); if(p._t2) p._t2.setAttribute('y',p.y+12);
  }
  function up(){
    document.removeEventListener('mousemove',move);
    document.removeEventListener('mouseup',up);
    if(el) el.setAttribute('class','hexpoly');
  }
  document.addEventListener('mousemove',move);
  document.addEventListener('mouseup',up);
}

// ---------- house-style windows ----------
let zTop=50; const houses=[];
function openHouse(node){
  if(document.getElementById('house-'+node.name)) return;
  const win=document.createElement('div'); win.className='house'; win.id='house-'+node.name;
  win.style.left=(70 + houses.length*34)+'px'; win.style.top=(70 + houses.length*26)+'px';
  win.innerHTML=
    '<div class="house-bar"><span class="house-title">'+node.name+
      ' <span style="color:'+node.color+'">['+node.plane+']</span></span>'+
      '<span class="house-btns"><span class="hb min">_</span><span class="hb max">□</span><span class="hb close">✕</span></span></div>'+
    '<div class="house-body">'+
      '<div class="w w1"><div class="wlab">W1 · product</div><div class="wcontent" id="w1-'+node.name+'"></div></div>'+
      '<div class="w w2"><div class="wlab">W2 · contributors / ideas posited</div><div class="wcontent" id="w2-'+node.name+'"></div></div>'+
      '<div class="w w3"><div class="wlab">W3 · 1d fold (2d/3d, shadow + overlay)</div><canvas id="w3-'+node.name+'"></canvas></div>'+
      '<div class="w w4"><div class="wlab">W4 · instrument (2d, running)</div><canvas id="w4-'+node.name+'"></canvas></div>'+
      '<div class="w w5"><div class="wlab">W5 · 3d (interactive)</div><canvas id="w5-'+node.name+'"></canvas></div>'+
    '</div>';
  document.getElementById('houses').appendChild(win);
  win.style.zIndex=++zTop;
  const bar=win.querySelector('.house-bar');
  // standard pointer-capture drag (works in all directions; webpage-first)
  bar.addEventListener('pointerdown',e=>{
    if(e.target.classList.contains('hb')) return;
    e.preventDefault();
    win.style.zIndex=++zTop;
    const sx=e.clientX, sy=e.clientY, ox=win.offsetLeft, oy=win.offsetTop;
    bar.setPointerCapture(e.pointerId);
    bar.style.cursor='grabbing';
    const mv=ev=>{ win.style.left=(ox+ev.clientX-sx)+'px'; win.style.top=(oy+ev.clientY-sy)+'px'; };
    const up2=ev=>{ bar.releasePointerCapture(e.pointerId); bar.style.cursor='move';
      bar.removeEventListener('pointermove',mv); bar.removeEventListener('pointerup',up2); };
    bar.addEventListener('pointermove',mv); bar.addEventListener('pointerup',up2);
  });
  win.querySelector('.close').onclick=()=>closeHouse(node.name);
  win.querySelector('.min').onclick=()=>{const b=win.querySelector('.house-body');b.style.display=b.style.display==='none'?'flex':'none';};
  win.querySelector('.max').onclick=()=>win.classList.toggle('max');
  document.getElementById('w1-'+node.name).innerHTML='<div class="desc">'+node.desc+'</div>';
  fetch('/agent?name='+encodeURIComponent(node.name)).then(r=>r.json()).then(d=>{
    const evs=(d&&d.events)?d.events:[];
    const ideas=[...new Set(evs.map(e=>e.proposed).filter(Boolean))];
    document.getElementById('w2-'+node.name).innerHTML=
      '<div class="kv">ideas posited: <b>'+(ideas.slice(0,14).join(', ')||'—')+'</b></div>'+
      '<div class="kv">ticks active: <b>'+evs.length+'</b></div>'+
      '<div class="kv">selected ★: <b>'+evs.filter(e=>e.selected).length+'</b></div>'+
      '<div class="kv">taught ✗: <b>'+evs.filter(e=>e.taught).length+'</b></div>';
  }).catch(()=>{document.getElementById('w2-'+node.name).innerHTML='<div class="kv">no history</div>';});
  const anims=[];
  anims.push(startW3(document.getElementById('w3-'+node.name), node));
  anims.push(startW4(document.getElementById('w4-'+node.name), node));
  if(node.kind==='core') anims.push(startPlanet(document.getElementById('w5-'+node.name)));
  else anims.push(startW5(document.getElementById('w5-'+node.name), node.color, node.kind));
  houses.push({name:node.name, anims});
}
function closeHouse(name){
  const win=document.getElementById('house-'+name); if(!win)return;
  const i=houses.findIndex(h=>h.name===name);
  if(i>=0){houses[i].anims.forEach(a=>a.dispose&&a.dispose());houses.splice(i,1);}
  win.remove();
}
// ---------- w3: 1d fold of 2d/3d (shadow + overlay) ----------
function startW3(canvas,node){
  const x=canvas.getContext('2d'); let t=0,raf;
  function fold(pts,ox,oy,sc,stroke){x.beginPath();pts.forEach((p,i)=>{const px=ox+p[0]*sc,py=oy+p[1]*sc*0.6;if(i===0)x.moveTo(px,py);else x.lineTo(px,py);});x.strokeStyle=stroke;x.lineWidth=2*devicePixelRatio;x.stroke();}
  function loop(){
    raf=requestAnimationFrame(loop);
    const W=canvas.width=canvas.clientWidth*devicePixelRatio, H=canvas.height=canvas.clientHeight*devicePixelRatio;
    x.fillStyle='#070d18';x.fillRect(0,0,W,H);
    const cx=W/2, cy=H/2, sc=Math.min(W,H)*0.3;
    const pts=[];for(let i=0;i<=120;i++){const u=i/120*Math.PI*2;pts.push([Math.sin(u*3+t),Math.sin(u*2+t*0.7+1),Math.cos(u*4+t*0.3)]);}
    fold(pts,cx+6*devicePixelRatio,cy+10*devicePixelRatio,sc,'rgba(60,90,140,0.35)');   // shadow
    fold(pts,cx,cy,sc,'#3af0cf');                                                        // main 1d fold
    fold(pts,cx+6*devicePixelRatio,cy+10*devicePixelRatio,sc,'rgba(98,169,255,0.18)');  // shadow overlay
    t+=0.02;
  }
  loop();return {dispose(){cancelAnimationFrame(raf);}};
}
// ---------- w4: 2d instrument running ----------
function startW4(canvas,node){
  const x=canvas.getContext('2d'); let t=0,raf; const fit=node._fit||0.5;
  function loop(){
    raf=requestAnimationFrame(loop);
    const W=canvas.width=canvas.clientWidth*devicePixelRatio, H=canvas.height=canvas.clientHeight*devicePixelRatio;
    x.fillStyle='#070d18';x.fillRect(0,0,W,H);
    x.beginPath();
    for(let i=0;i<=W;i+=2){const v=Math.sin(i*0.03+t)*0.4*fit+Math.sin(i*0.011+t*1.7)*0.3*(1-fit)+(Math.random()-0.5)*0.05;const y=H/2-v*H*0.4;if(i===0)x.moveTo(i,y);else x.lineTo(i,y);}
    x.strokeStyle='#ffd166';x.lineWidth=2*devicePixelRatio;x.stroke();
    x.fillStyle='#8298c6';x.font=(11*devicePixelRatio)+'px monospace';
    x.fillText('running: '+(node.proposed||'—')+'  fit '+(node._fit||0).toFixed(2),8*devicePixelRatio,H-8*devicePixelRatio);
    t+=0.08;
  }
  loop();return {dispose(){cancelAnimationFrame(raf);}};
}
// ---------- w5: interactive 3d ----------
function startW5(canvas,color,kind){
  if(typeof THREE==='undefined'){canvas.parentNode.insertAdjacentHTML('beforeend','<div class=log">THREE.js not loaded</div>');return {dispose(){}};}
  const r=new THREE.WebGLRenderer({canvas,antialias:true}); r.setPixelRatio(Math.min(devicePixelRatio,2));
  const sc=new THREE.Scene(); sc.fog=new THREE.FogExp2(0x05070c,0.02);
  const cam=new THREE.PerspectiveCamera(50,1,0.1,100); cam.position.set(0,0,4);
  sc.add(new THREE.AmbientLight(0x5577aa,0.8));
  const pl=new THREE.PointLight(0x3af0cf,1.3,50); pl.position.set(3,3,3); sc.add(pl);
  const col=parseInt(color.replace('#','0x'));
  const geo=kind==='core'?new THREE.IcosahedronGeometry(1.15,1):new THREE.IcosahedronGeometry(0.9,0);
  const mesh=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:col,emissive:col,emissiveIntensity:0.25,metalness:0.4,roughness:0.45,flatShading:true}));
  sc.add(mesh);
  const wire=new THREE.LineSegments(new THREE.WireframeGeometry(geo),new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:0.22}));
  sc.add(wire);
  let drag=false,lx=0,ly=0,tx=0,ty=0;
  canvas.addEventListener('mousedown',e=>{drag=true;lx=e.clientX;ly=e.clientY;});
  addEventListener('mouseup',()=>drag=false);
  addEventListener('mousemove',e=>{if(drag&&canvas){tx+=(e.clientX-lx)*0.01;ty+=(e.clientY-ly)*0.01;lx=e.clientX;ly=e.clientY;}});
  let raf;
  function loop(){raf=requestAnimationFrame(loop);const rc=canvas.getBoundingClientRect();if(rc.width>0){r.setSize(rc.width,rc.height,false);cam.aspect=rc.width/rc.height;cam.updateProjectionMatrix();}if(!drag)tx+=0.006;mesh.rotation.set(ty,tx,0);wire.rotation.copy(mesh.rotation);r.render(sc,cam);}
  loop();
  return {dispose(){cancelAnimationFrame(raf);if(r.forceContextLoss)r.forceContextLoss();r.dispose();}};
}
// ---------- w5 (BIOSPHERE): live 3d planet ----------
function startPlanet(canvas){
  if(typeof THREE==='undefined'){canvas.parentNode.insertAdjacentHTML('beforeend','<div class=log">THREE.js not loaded</div>');return {dispose(){}};}
  const r=new THREE.WebGLRenderer({canvas,antialias:true}); r.setPixelRatio(Math.min(devicePixelRatio,2));
  const sc=new THREE.Scene(); sc.fog=new THREE.FogExp2(0x05070c,0.0016);
  const cam=new THREE.PerspectiveCamera(55,1,0.1,5000); cam.position.set(0,120,460);
  sc.add(new THREE.AmbientLight(0x5577aa,0.7));
  const p=new THREE.PointLight(0x3af0cf,1.2,2000); p.position.set(0,0,0); sc.add(p);
  const pl=new THREE.PointLight(0xffd166,0.6,2000); pl.position.set(0,300,0); sc.add(pl);
  [[182,'#62a9ff',0.10],[130,'#3af0cf',0.12],[78,'#b78cff',0.16],[24,'#ffd166',0.30]].forEach(([rr,c,o])=>{
    sc.add(new THREE.Mesh(new THREE.SphereGeometry(rr,40,28),new THREE.MeshBasicMaterial({color:c,wireframe:true,transparent:true,opacity:o})));
  });
  const core=new THREE.Mesh(new THREE.SphereGeometry(10,24,18),new THREE.MeshBasicMaterial({color:0xffd166})); sc.add(core);
  const nodeMesh={}; let theta=0.5,phi=0.6,dist=460,drag=false,lx=0,ly=0,R=0;
  canvas.addEventListener('mousedown',e=>{drag=true;lx=e.clientX;ly=e.clientY;});
  addEventListener('mouseup',()=>drag=false);
  addEventListener('mousemove',e=>{if(drag){theta-=(e.clientX-lx)*0.005;phi=Math.max(0.15,Math.min(1.5,phi-(e.clientY-ly)*0.005));lx=e.clientX;ly=e.clientY;}});
  function sync(){const pop=(lastStatic.population||[]);pop.forEach((m,i)=>{if(!nodeMesh[m.name]){const sh={L1:182,L2:130,L3:78,L4:24,H:156}[m.plane]||182;const mesh=new THREE.Mesh(new THREE.SphereGeometry(6,16,12),new THREE.MeshBasicMaterial({color:m.plane==='L1'?0x62a9ff:m.plane==='L2'?0x3af0cf:m.plane==='H'?0xffd166:0xffffff}));sc.add(mesh);nodeMesh[m.name]=mesh;}const sh={L1:182,L2:130,L3:78,L4:24,H:156}[m.plane]||182;const a=i*1.7;nodeMesh[m.name].position.set(Math.cos(a)*sh,Math.sin(a*1.3)*sh*0.7,Math.sin(a)*sh);});}
  let raf;
  function loop(){raf=requestAnimationFrame(loop);const rc=canvas.getBoundingClientRect();if(rc.width>0){r.setSize(rc.width,rc.height,false);cam.aspect=rc.width/rc.height;cam.updateProjectionMatrix();}cam.position.set(Math.sin(theta)*Math.cos(phi)*dist,Math.sin(phi)*dist,Math.cos(theta)*Math.cos(phi)*dist);cam.lookAt(0,0,0);R+=0.0025;core.rotation.y=R;sync();r.render(sc,cam);}
  loop();
  return {dispose(){cancelAnimationFrame(raf);if(r.forceContextLoss)r.forceContextLoss();r.dispose();}};
}
// ---------- chart ----------
function drawChart(hist){
  const c=document.getElementById('chart'),x=c.getContext('2d');
  c.width=c.clientWidth*devicePixelRatio;c.height=c.clientHeight*devicePixelRatio;
  x.clearRect(0,0,c.width,c.height);
  const h=hist||[]; if(!h.length)return;
  const W=c.width,H=c.height,pad=10;
  x.strokeStyle='#1c2940';x.beginPath();x.moveTo(0,H/2);x.lineTo(W,H/2);x.stroke();
  x.beginPath();
  h.forEach((v,i)=>{const px=pad+i/(Math.max(1,h.length-1))*(W-2*pad);const py=H/2-(v)*(H/2-pad);if(i===0)x.moveTo(px,py);else x.lineTo(px,py);});
  x.strokeStyle='#3af0cf';x.lineWidth=2*devicePixelRatio;x.stroke();
  x.fillStyle='#3af0cf';x.font=(11*devicePixelRatio)+'px monospace';
  x.fillText('learned L4 weight ('+h[h.length-1].toFixed(3)+')',pad,H-6*devicePixelRatio);
}
// ---------- UI render ----------
function tab(id,el){document.querySelectorAll('.tabs button').forEach(b=>b.classList.remove('on'));if(el)el.classList.add('on');
  ['genome','pop','gov','herm','zones','log'].forEach(t=>document.getElementById('tab-'+t).style.display=t===id?'block':'none');}
function render(S){
  document.getElementById('tk').textContent='tick '+S.tick;
  document.getElementById('k2').textContent=S.tick;
  document.getElementById('d2').textContent=S.differences_ticks;
  document.getElementById('p2').textContent=(S.population||[]).length;
  document.getElementById('v2').textContent=(S.verdicts||[]).length;
  const lw=S.learned_weight||0; document.getElementById('wgt').textContent='L4 weight '+lw.toFixed(3);
  document.getElementById('hm').textContent='HERMES '+(S.hermes.curiosity||0).toFixed(2);
  document.getElementById('genome').innerHTML=(S.genome||[]).slice(-16).map(g=>
    '<span class=chip><b>'+(g.toward||'?')+'</b> <small>w:'+(g.weight||0).toFixed(2)+'</small></span>').join('');
  document.getElementById('pop').innerHTML='<table><tr><th>name</th><th>plane</th><th>fit</th><th>gen</th></tr>'+
    (S.population||[]).map(p=>`<tr class="prow" data-name="${p.name}" data-plane="${p.plane}" style="cursor:pointer"><td>${p.name}</td><td class=${p.plane}>${p.plane}</td><td>${p.fitness}</td><td>${p.gen}</td></tr>`).join('')+'</table>';
  document.querySelectorAll('#pop .prow').forEach(tr=>tr.addEventListener('click',()=>{
    const nm=tr.getAttribute('data-name'), pl=tr.getAttribute('data-plane');
    openHouse({name:nm, plane:pl, kind:(pl==='L1'?'agent':pl==='L2'?'subagent':'hermes'),
      color:planeColor(pl), desc:planeDesc(pl), metric:'fit '+((S.population.find(x=>x.name===nm)||{}).fitness!=null?(S.population.find(x=>x.name===nm)||{}).fitness:'?'), proposed:(S.population.find(x=>x.name===nm)||{}).proposed||'', _fit:(parseFloat((S.population.find(x=>x.name===nm)||{}).fitness)||0.5)});
  }));
  document.getElementById('gov').innerHTML=(S.govern||[]).slice().reverse().map(g=>
    '<span class=hl>verdict '+(g.verdict||'?')+'</span> distinct '+JSON.stringify(g.distinct)+' taught '+JSON.stringify(g.taught)+'<br>pop '+JSON.stringify(g.population)+'<br><br>').join('')||'no governance yet';
  const h=S.hermes||{};
  document.getElementById('herm').innerHTML='<span class=chip><b>skills</b> <small>'+(h.skills||[]).join(', ')+'</small></span>\n     <span class=chip><b>curiosity</b> <small>'+(h.curiosity||0).toFixed(3)+'</small></span>\n     <span class=chip><b>retention</b> <small>'+(h.retention||0)+'</small></span>\n     <div class=log style="margin-top:8px">recall:<br>'+JSON.stringify(h.last||[],null,1)+'</div>';
  document.getElementById('clog').innerHTML=(S.capsule_log||[]).reverse().map(c=>
    '<span class=hl>'+c[0]+'</span> · '+c[1]).join('<br>');
  const z=S.zones;
  if(z){
    document.getElementById('zones').innerHTML=
      '<div class="chip"><b>SEALED</b> <small>'+(z.sealed?'yes':'no')+'</small></div>'+
      '<div class=chip><b>z1 \\ l0</b> <small>'+z.z1+'</small></div>'+
      '<div class=chip><b>z2 \\ l1</b> <small>'+z.z2+'</small></div>'+
      '<div class=chip><b>z3 \\ l2</b> <small>'+z.z3+'</small></div>'+
      (z.sovereign_veto?'<div class=log style="margin-top:8px;color:var(--warn)">⛔ SOVEREIGN VETO (wall): '+z.sovereign_veto+'</div>'
                        :'<div class=log style="margin-top:8px;color:var(--acc)">✓ no sovereign veto — verdict passes the wall</div>')+
      '<div class=log style="margin-top:6px">democratic (z2) verdict: '+(z.democratic||'none')+'</div>'+
      '<div class=log">stewardship (z3) pass: '+z.stewardship_pass+'</div>'+
      '<div class=log">seal_ok: '+z.seal_ok+'</div>'+
      '<div class=log" style="margin-top:6px;color:var(--gold)">"'+z.doctrine+'"</div>'+
      '<div class=log" style="margin-top:6px">'+z.report.join('<br>')+'</div>';
  }
  drawChart(S.weight_history);
  document.getElementById('playdot').className='dot'+(S.playing?' live':' off');
  document.getElementById('live').textContent=S.playing?'streaming…':'idle';
  drawHex(buildNodes(S));
}
function togglePlay(){fetch('/play');}
function stepRun(n){fetch('/run?n='+n+'&reset=false');}
function resetRun(){fetch('/run?n=0&reset=true');}
function speciate(t){fetch('/speciate?ticks='+t).then(r=>r.json()).then(j=>alert('Speciation: '+JSON.stringify(j)));}
function setSpeed(v){fetch('/speed?v='+v);}
// ---------- Tier 1: live SSE stream ----------
let es, lastStatic={};
function connectStream(){
  es=new EventSource('/stream');
  es.onopen=()=>{document.getElementById('live').textContent='connected';document.getElementById('playdot').className='dot live';};
  es.onmessage=(ev)=>{
    const S=JSON.parse(ev.data); lastStatic=S;
    render(S);
    document.getElementById('live').textContent='streaming…';
  };
  es.onerror=()=>{document.getElementById('live').textContent='reconnecting…';};
}
function tickStatic(){fetch('/state').then(r=>r.json()).then(S=>{lastStatic=S;if(!es)render(S);});}
connectStream(); setInterval(tickStatic,2000); tickStatic();
</script></body></html>"""

def _build_spinor_svg():
    """Genuine parametric Möbius strip — the SU(2) spinor object: a single
    half-twisted band. One full 360deg rotation flips it (spinor sign flip);
    two full turns (720deg) return it to start. Geometry is computed, not drawn."""
    import math
    R, w, N = 22.0, 6.0, 180
    cx0 = cy0 = 32.0
    top, bot, cen = [], [], []
    for i in range(N + 1):
        u = 2.0 * math.pi * i / N
        c, s = math.cos(u / 2.0), math.sin(u / 2.0)
        cu, su = math.cos(u), math.sin(u)
        xc, yc = R * cu, R * su                       # centerline (a circle)
        cen.append((cx0 + xc, cy0 + (yc * 0.62)))
        for sign, store in ((1.0, top), (-1.0, bot)): # two ribbon edges
            rr = R + sign * w * c
            x = rr * cu
            y = rr * su
            z = sign * w * s
            sx = cx0 + x
            sy = cy0 + (y * 0.62 - z * 0.55)          # tilt projection so the twist reads
            store.append((round(sx, 1), round(sy, 1)))
    def pts(lst):
        return " ".join(f"{x},{y}" for x, y in lst)
    d = "M " + pts(top) + " L " + pts(list(reversed(bot))) + " Z"
    dc = "M " + pts(cen)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        '<defs><linearGradient id="sg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#3af0cf"/>'
        '<stop offset="0.5" stop-color="#1fb89e"/>'
        '<stop offset="1" stop-color="#0e6b63"/></linearGradient></defs>'
        '<g>'
        '<path d="' + d + '" fill="url(#sg)" stroke="#3af0cf" stroke-width="0.8" '
        'stroke-linejoin="round" opacity="0.92"/>'
        '<path d="' + dc + '" fill="none" stroke="#0a0f1a" stroke-width="0.7" opacity="0.5"/>'
        '<animateTransform attributeName="transform" type="rotate" '
        'from="0 32 32" to="360 32 32" dur="8s" repeatCount="indefinite"/>'
        '</g></svg>'
    )
SPINOR_SVG = _build_spinor_svg()


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
        path = self.path.split("?")[0]
        if path == "/stream":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            # initial snapshot so the canvas isn't empty
            snap = state_snapshot()
            snap["members"] = snap["population"]
            try:
                self.wfile.write(f"data: {json.dumps(snap)}\n\n".encode())
            except Exception:
                pass
            while True:
                try:
                    item = _BROADCAST.get(timeout=30)
                    self.wfile.write(f"data: {json.dumps(item)}\n\n".encode())
                    self.wfile.flush()
                except queue.Empty:
                    try:
                        self.wfile.write(b": ping\n\n")
                    except Exception:
                        break
                except Exception:
                    break
            return
        if path == "/state":
            self._send(200, json.dumps(state_snapshot()))
        elif path == "/agent":
            q = up.parse_qs(up.urlparse(self.path).query)
            name = q.get("name", [""])[0]
            hist = _load("agent_history.json", {})
            # case-insensitive lookup (3D node stores "hermes"; population rows store "HERMES")
            dossier = hist.get(name) or next((v for k, v in hist.items() if k.lower() == name.lower()), None)
            self._send(200, json.dumps(dossier or {}))
        elif path == "/run":
            q = up.parse_qs(up.urlparse(self.path).query)
            n = int(q.get("n", ["10"])[0]); reset = q.get("reset", ["false"])[0] == "true"
            if reset and n == 0:
                import shutil
                cd = os.path.join(STATE, "capsules")
                if os.path.isdir(cd): shutil.rmtree(cd); os.makedirs(cd)
                for f in ("ledger.json", "learned.json", "differences.json", "population.json",
                          "learned_weight.json", "weight_history.json", "hermes.json", "tick.json",
                          "agent_history.json"):
                    p = os.path.join(STATE, f)
                    if os.path.isfile(p): os.remove(p)
                self._send(200, json.dumps({"ok": True, "reset": True}))
            else:
                threading.Thread(target=run_pulse_bg, args=(n, reset), daemon=True).start()
                self._send(200, json.dumps({"ok": True, "n": n, "reset": reset}))
        elif path == "/play":
            sp = max(1, int(_TRANS["speed"]))
            threading.Thread(target=run_pulse_bg, args=(sp, False), daemon=True).start()
            self._send(200, json.dumps({"ok": True, "playing": True}))
        elif path == "/speed":
            q = up.parse_qs(up.urlparse(self.path).query)
            _TRANS["speed"] = int(q.get("v", ["3"])[0])
            self._send(200, json.dumps({"speed": _TRANS["speed"]}))
        elif path == "/speciate":
            q = up.parse_qs(up.urlparse(self.path).query)
            t = int(q.get("ticks", ["5"])[0])
            res = speciate_bg(t)
            self._send(200, json.dumps(res or {}))
        elif path == "/hermes":
            hm = Hermes(STATE)
            self._send(200, json.dumps({"skills": hm.skills, "curiosity": hm.curiosity,
                                        "retention": len(hm.retention), "last": hm.recall(4)}))
        elif path in ("/", "/index.html"):
            html = HTML.replace("/*__THREE__*/", THREE_JS or "console.warn('three.min.js missing')")
            self._send(200, html, "text/html")
        elif path == "/favicon.svg":
            self._send(200, SPINOR_SVG, "image/svg+xml")
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def log_message(self, *a):
        pass


def pick_port(preferred=PORT):
    """Bind a free port, preferring `preferred`, else 8760-8799.
    Returns (bound ThreadingHTTPServer, port) or (None, None) if nothing is free."""
    for cand in [preferred] + list(range(8760, 8800)):
        try:
            return ThreadingHTTPServer(("127.0.0.1", cand), Handler), cand
        except OSError:
            continue
    return None, None


def main():
    srv, port = pick_port()
    if srv is None:
        print("Could not bind any port in 8753,8760-8799")
        return
    print(f"Slaughterhouse5 console -> http://127.0.0.1:{port}/")
    print("  Honeycomb + house-style windows (w1-w5) + live SSE stream. Run/Step/Reset/Speciate/speed.")
    try:
        webbrowser.open(f"http://127.0.0.1:{port}/")
    except Exception:
        pass
    srv.serve_forever()


if __name__ == "__main__":
    main()
