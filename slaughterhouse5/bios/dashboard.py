"""Local dashboard for the Slaughterhouse5 biosphere — interactive WebGL console.

Real 3D via bundled Three.js (bios/static/three.min.js, works offline). An
"enterprise" toolsuite with live tabs, a time-series chart of the learned L4
weight, play/pause/step/speed transport, and clickable agents.

  Run:   python -m bios.dashboard     (then open the printed URL)
  Win:   run-biosphere.bat
"""
from __future__ import annotations

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from .kernel import BioSphere
from . import pulse
from .hermes import Hermes, NOVEL_POOL

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state")
STATIC = os.path.join(HERE, "static")
PORT = int(os.environ.get("BIOS_PORT", "8753"))

_run_lock = threading.Lock()

# transport shared state (set by /run, read by UI)
_TRANS = {"playing": False, "speed": 1.0, "last_run": 0}


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


def run_pulse_bg(n: int, reset: bool = False):
    with _run_lock:
        _TRANS["playing"] = True
        pulse.run_pulse(BioSphere(), n=n, verbose=False, reset=reset)
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
    # per-tick L4 weight series from ledger or weight history file
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
        "capsule_log": [(c.get("kind"), c.get("sender")) for c in _capsules()][-30:],
        "hermes": hm,
        "playing": _TRANS["playing"],
        "speed": _TRANS["speed"],
    }


def write_weight_history():
    """record the current learned weight into a rolling history file."""
    hist = _load("weight_history.json", [])
    hist.append(round(_load("learned_weight.json", 0.6), 4))
    json.dump(hist[-120:], open(os.path.join(STATE, "weight_history.json"), "w"), indent=0)


HTML = r"""<!doctype html><html><head><meta charset=utf-8>
<title>Slaughterhouse5 — Biosphere Console</title>
<style>
  :root{--bg:#05070c;--panel:#0c1320;--edge:#1c2940;--fg:#e3ecff;--mut:#8298c6;
        --acc:#3af0cf;--warn:#ff6b6b;--gold:#ffd166;--blue:#62a9ff;--teal:#3af0cf;--pur:#b78cff}
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);
            font:13px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;overflow:hidden}
  #app{display:grid;grid-template-rows:48px 1fr 30px;height:100%}
  header{display:flex;align-items:center;gap:12px;padding:0 16px;border-bottom:1px solid var(--edge);
         background:linear-gradient(90deg,#0a1120,#0c1320)}
  h1{font-size:15px;margin:0;color:var(--acc);letter-spacing:2px}
  .pill{background:#0f1a2c;border:1px solid var(--edge);border-radius:999px;padding:3px 10px;color:var(--mut);font-size:12px}
  .grow{flex:1}
  .transport button{background:#13233a;color:var(--fg);border:1px solid var(--edge);border-radius:7px;padding:6px 11px;margin-left:5px;cursor:pointer}
  .transport button:hover{border-color:var(--acc);color:var(--acc)}
  main{display:grid;grid-template-columns:minmax(380px,1.05fr) 1.25fr;gap:10px;padding:10px;overflow:hidden}
  .panel{background:var(--panel);border:1px solid var(--edge);border-radius:12px;padding:10px;overflow:hidden;position:relative;display:flex;flex-direction:column}
  .panel h2{margin:0 0 8px;font-size:10px;color:var(--mut);text-transform:uppercase;letter-spacing:1.5px}
  #glwrap{flex:1;position:relative;border-radius:10px;overflow:hidden;background:radial-gradient(600px 400px at 50% 40%,#0e1a30,#05070c)}
  #gl{width:100%;height:100%;display:block}
  #selinfo{position:absolute;left:10px;bottom:10px;background:rgba(8,14,24,.85);border:1px solid var(--edge);
           border-radius:8px;padding:8px;font-size:12px;max-width:60%;display:none}
  .tabs{display:flex;gap:6px;margin-bottom:8px}
  .tabs button{background:#0f1a2c;border:1px solid var(--edge);color:var(--mut);border-radius:7px;padding:5px 10px;cursor:pointer;font-size:12px}
  .tabs button.on{color:var(--acc);border-color:var(--acc)}
  .tabbody{flex:1;overflow:auto}
  table{width:100%;border-collapse:collapse} td,th{text-align:left;padding:4px 7px;border-bottom:1px solid #14202f;font-size:12px}
  .L1{color:var(--blue)} .L2{color:var(--teal)} .H{color:var(--gold)} .L4{color:var(--gold)}
  .chip{display:inline-block;margin:3px;padding:4px 9px;border-radius:7px;background:#12233a;border:1px solid var(--edge);font-size:12px}
  .chip b{color:var(--acc)} .chip small{color:var(--mut)}
  .kpis{display:flex;gap:16px;margin-bottom:8px}
  .kpis div{font-size:11px;color:var(--mut)} .kpis b{color:var(--fg);font-size:16px}
  #chart{width:100%;height:130px;background:#070d18;border:1px solid var(--edge);border-radius:8px}
  .log{font-size:12px;color:var(--mut);white-space:pre-wrap}
  .log .hl{color:var(--acc)} .log .w{color:var(--gold)}
  #status{font-size:11px;color:var(--mut);padding:0 14px;border-top:1px solid var(--edge);display:flex;align-items:center;gap:14px}
  .dot{width:8px;height:8px;border-radius:50%;background:var(--acc);display:inline-block;box-shadow:0 0 8px var(--acc)}
  .dot.off{background:#3a4a63;box-shadow:none}
</style></head><body><div id=app>
<header>
  <h1>SLAUGHTERHOUSE5</h1><span class=pill id=tk>tick 0</span>
  <span class=pill id=wgt>L4 weight 0.00</span><span class=pill id=hm>HERMES 0.50</span>
  <span class=grow></span>
  <span class=transport>
    <button id=play onclick=togglePlay()>▶ Run</button>
    <button onclick=stepRun(1)>Step</button>
    <button onclick=resetRun()>Reset</button>
    <button onclick=speciate(5)>⚡ Speciate</button>
    <label style="color:var(--mut)">speed <input id=spd type=range min=1 max=10 value=3 style="vertical-align:middle" oninput="setSpeed(this.value)"></label>
  </span>
</header>
<main>
  <div class=panel><h2>Biosphere — WebGL (L1→L4, click an agent)</h2>
    <div id=glwrap><canvas id=gl></canvas><div id=selinfo></div></div>
  </div>
  <div class=panel><h2>Toolsuite</h2>
    <div class=tabs>
      <button class=on onclick=tab('genome',this)>Genome + L4</button>
      <button onclick=tab('pop',this)>Population</button>
      <button onclick=tab('gov',this)>Governance</button>
      <button onclick=tab('herm',this)>Hermes</button>
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
    <div class=tabbody id=tab-log style="display:none"><div id=clog class=log></div></div>
  </div>
</main>
<div id=status><span><span class="dot off" id=playdot></span> idle</span><span id=stmsg></span><span class=grow></span><span>drag to orbit · scroll to zoom · click agent to inspect</span></div>
</div>

<script src="/static/three.min.js"></script>
<script>
// ---------- WebGL scene ----------
const cv=document.getElementById('gl'); let renderer,scene,camera,ray,core,picks=[];
function initGL(){
  renderer=new THREE.WebGLRenderer({canvas:cv,antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  scene=new THREE.Scene(); scene.fog=new THREE.FogExp2(0x05070c,0.0016);
  camera=new THREE.PerspectiveCamera(55,1,0.1,5000); camera.position.set(0,120,460);
  scene.add(new THREE.AmbientLight(0x5577aa,0.7));
  const p=new THREE.PointLight(0x3af0cf,1.2,2000); p.position.set(0,0,0); scene.add(p);
  const pl=new THREE.PointLight(0xffd166,0.6,2000); pl.position.set(0,300,0); scene.add(pl);
  // shells L1 L2 L3 L4 (+H)
  const shells=[[182,'#62a9ff',0.10],[130,'#3af0cf',0.12],[78,'#b78cff',0.16],[24,'#ffd166',0.30]];
  for(const [r,c,o] of shells){
    const g=new THREE.SphereGeometry(r,40,28);
    const m=new THREE.MeshBasicMaterial({color:c,wireframe:true,transparent:true,opacity:o});
    scene.add(new THREE.Mesh(g,m));
  }
  const cg=new THREE.SphereGeometry(10,24,18);
  core=new THREE.Mesh(cg,new THREE.MeshBasicMaterial({color:0xffd166})); scene.add(core);
  ray=new THREE.Raycaster();
}
let R=0; const nodeMesh={};
function syncNodes(S){
  // remove old
  for(const k in nodeMesh){scene.remove(nodeMesh[k]); delete nodeMesh[k];}
  picks=[];
  const pop=(S.population||[]);
  const shells={L1:182,L2:130,L3:78,L4:24,H:156};
  pop.forEach((m,i)=>{
    const sh=shells[m.plane]||182; const a=i*1.7;
    const x=Math.cos(a)*sh,y=Math.sin(a*1.3)*sh*0.7,z=Math.sin(a)*sh;
    const col=m.plane==='L1'?0x62a9ff:m.plane==='L2'?0x3af0cf:m.plane==='H'?0xffd166:0xffffff;
    const mesh=new THREE.Mesh(new THREE.SphereGeometry(6,16,12),new THREE.MeshBasicMaterial({color:col}));
    mesh.position.set(x,y,z); mesh.userData={name:m.name,plane:m.plane,fit:m.fitness,gen:m.gen};
    scene.add(mesh); nodeMesh[m.name]=mesh; picks.push(mesh);
  });
  if(S.hermes&&S.hermes.skills){
    const mesh=new THREE.Mesh(new THREE.SphereGeometry(8,16,12),new THREE.MeshBasicMaterial({color:0xffd166}));
    mesh.position.set(Math.cos(0.6)*156,Math.sin(0.6)*156,Math.sin(0.6)*156*0.7);
    mesh.userData={name:'HERMES',plane:'H',curiosity:S.hermes.curiosity,retention:S.hermes.retention};
    scene.add(mesh); nodeMesh['HERMES']=mesh; picks.push(mesh);
  }
}
function pick(ev){
  const r=cv.getBoundingClientRect();
  const m=new THREE.Vector2(((ev.clientX-r.left)/r.width)*2-1,-((ev.clientY-r.top)/r.height)*2+1);
  ray.setFromCamera(m,camera);
  const hit=ray.intersectObjects(picks)[0];
  if(hit){const d=hit.object.userData;const el=document.getElementById('selinfo');
    el.style.display='block';
    el.innerHTML=`<b style="color:var(--gold)">${d.name}</b> <span class=${d.plane}>[${d.plane}]</span><br>`+
      (d.plane==='H'?`curiosity ${d.curiosity} · retention ${d.retention}`:`fitness ${d.fit} · gen ${d.gen}`);}
}
cv.addEventListener('click',pick);
// orbit controls (minimal, inline)
let drag=false,lx=0,ly=0,theta=0.5,phi=0.6,dist=460;
function orbit(dx,dy){theta-=dx*0.005;phi=Math.max(0.15,Math.min(1.5,phi-dy*0.005));}
cv.addEventListener('mousedown',e=>{drag=true;lx=e.clientX;ly=e.clientY;});
addEventListener('mouseup',()=>drag=false);
addEventListener('mousemove',e=>{if(drag){orbit(e.clientX-lx,e.clientY-ly);lx=e.clientX;ly=e.clientY;}});
cv.addEventListener('wheel',e=>{dist=Math.max(120,Math.min(1200,dist+e.deltaY*0.3));e.preventDefault();},{passive:false});
function renderGL(S){
  if(!renderer)return;
  const r=cv.getBoundingClientRect();
  renderer.setSize(r.width,r.height,false);
  camera.position.set(Math.sin(theta)*Math.cos(phi)*dist,Math.sin(phi)*dist,Math.cos(theta)*Math.cos(phi)*dist);
  camera.lookAt(0,0,0);
  R+=0.0025; core.rotation.y=R; syncNodes(S);
  renderer.render(scene,camera);
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
  h.forEach((v,i)=>{const px=pad+i/(Math.max(1,h.length-1))*(W-2*pad);const py=H/2-(v)* (H/2-pad);
    if(i===0)x.moveTo(px,py);else x.lineTo(px,py);});
  x.strokeStyle='#3af0cf';x.lineWidth=2*devicePixelRatio;x.stroke();
  x.fillStyle='#3af0cf';x.font=`${11*devicePixelRatio}px monospace`;
  x.fillText('learned L4 weight  ('+h[h.length-1].toFixed(3)+')',pad,H-6*devicePixelRatio);
}
// ---------- UI helpers ----------
function tab(id,el){document.querySelectorAll('.tabs button').forEach(b=>b.classList.remove('on'));el.classList.add('on');
  ['genome','pop','gov','herm','log'].forEach(t=>document.getElementById('tab-'+t).style.display=t===id?'block':'none');}
function render(S){
  document.getElementById('tk').textContent='tick '+S.tick;
  document.getElementById('k2').textContent=S.tick;
  document.getElementById('d2').textContent=S.differences_ticks;
  document.getElementById('p2').textContent=(S.population||[]).length;
  document.getElementById('v2').textContent=(S.verdicts||[]).length;
  const lw=S.learned_weight||0; document.getElementById('wgt').textContent='L4 weight '+lw.toFixed(3);
  document.getElementById('hm').textContent='HERMES '+(S.hermes.curiosity||0).toFixed(2);
  document.getElementById('genome').innerHTML=(S.genome||[]).slice(-16).map(g=>
    `<span class=chip><b>${g.toward||'?'}</b> <small>w:${(g.weight||0).toFixed(2)}</small></span>`).join('');
  document.getElementById('pop').innerHTML='<table><tr><th>name</th><th>plane</th><th>fit</th><th>gen</th></tr>'+
    (S.population||[]).map(p=>`<tr><td>${p.name}</td><td class=${p.plane}>${p.plane}</td><td>${p.fitness}</td><td>${p.gen}</td></tr>`).join('')+'</table>';
  document.getElementById('gov').innerHTML=(S.govern||[]).slice().reverse().map(g=>
    `<span class=hl>verdict ${g.verdict||'?'}</span> distinct ${JSON.stringify(g.distinct)} taught ${JSON.stringify(g.taught)}<br>pop ${JSON.stringify(g.population)}<br><br>`).join('')||'no governance yet';
  const h=S.hermes||{};
  document.getElementById('herm').innerHTML=`<span class=chip><b>skills</b> <small>${(h.skills||[]).join(', ')}</small></span>
     <span class=chip><b>curiosity</b> <small>${(h.curiosity||0).toFixed(3)}</small></span>
     <span class=chip><b>retention</b> <small>${h.retention||0}</small></span>
     <div class=log style="margin-top:8px">recall:<br>${JSON.stringify(h.last||[],null,1)}</div>`;
  document.getElementById('clog').innerHTML=(S.capsule_log||[]).reverse().map(c=>
    `<span class=hl>${c[0]}</span> · ${c[1]}`).join('<br>');
  drawChart(S.weight_history);
  document.getElementById('playdot').className='dot'+(S.playing?'':' off');
  document.getElementById('stmsg').textContent=S.playing?'running…':'idle';
}
function togglePlay(){fetch('/play');}
function stepRun(n){fetch('/run?n='+n+'&reset=false');}
function resetRun(){fetch('/run?n=0&reset=true');}
function speciate(t){fetch('/speciate?ticks='+t).then(r=>r.json()).then(j=>alert('Speciation: '+JSON.stringify(j)));}
function setSpeed(v){fetch('/speed?v='+v);}
function tick(){fetch('/state').then(r=>r.json()).then(S=>{renderGL(S);render(S);});}
function loop(){tick();setTimeout(loop,700);}
initGL(); loop();
</script></body></html>"""


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
        if path.startswith("/static/"):
            fp = os.path.join(STATIC, os.path.basename(path))
            if os.path.isfile(fp):
                with open(fp, "rb") as f:
                    self._send(200, f.read(), "application/javascript")
            else:
                self._send(404, b"not found", "text/plain")
            return
        if path == "/state":
            self._send(200, json.dumps(state_snapshot()))
        elif path == "/run":
            q = up.parse_qs(up.urlparse(self.path).query)
            n = int(q.get("n", ["10"])[0]); reset = q.get("reset", ["false"])[0] == "true"
            if reset and n == 0:
                # reset only: clear state dir
                import shutil
                cd = os.path.join(STATE, "capsules")
                if os.path.isdir(cd): shutil.rmtree(cd); os.makedirs(cd)
                for f in ("ledger.json", "learned.json", "differences.json", "population.json",
                          "learned_weight.json", "weight_history.json", "hermes.json"):
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
            self._send(200, HTML, "text/html")
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def log_message(self, *a):
        pass


def main():
    import webbrowser
    srv = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Slaughterhouse5 console -> http://127.0.0.1:{PORT}/")
    print("  WebGL planet + enterprise toolsuite. Run / Step / Reset / Speciate / speed.")
    try:
        webbrowser.open(f"http://127.0.0.1:{PORT}/")
    except Exception:
        pass
    srv.serve_forever()


if __name__ == "__main__":
    main()
