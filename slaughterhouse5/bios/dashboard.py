"""Local dashboard for the Slaughterhouse5 biosphere.

Serves a live web view of the biosphere's state over HTTP and can trigger
PULSE runs.  Run:   python -m bios.dashboard   (then open the printed URL)
Windows:            run-biosphere.bat

The dashboard reads the git-versioned state/ files, so it reflects exactly what
the biosphere has persisted -- no separate database.
"""
from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from .kernel import BioSphere
from . import pulse

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


def state_snapshot():
    ledger = _load("ledger.json", {})
    diffs = _load("differences.json", [])
    return {
        "tick": ledger.get("ticks", 0),
        "genome": _load("learned.json", []),
        "population": _load("population.json", []),
        "differences_ticks": len(diffs),
        "last_differing_pairs": diffs[-1].get("differing_pairs", []) if diffs else [],
        "learned_weight": _load("learned_weight.json", 0.6),
        "verdicts": [d.get("verdict") for d in diffs],
    }


def run_pulse_bg(n: int, reset: bool = False):
    with _run_lock:
        pulse.run_pulse(BioSphere(), n=n, verbose=False, reset=reset)


HTML = r"""<!doctype html><meta charset=utf-8><title>Slaughterhouse5 — biosphere dashboard</title>
<style>
  :root{--bg:#0c0f14;--fg:#dfe7ff;--mut:#8aa0c8;--acc:#54e0c8;--warn:#ff7a7a}
  *{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--fg);
    font:14px/1.5 ui-monospace,Menlo,Consolas,monospace}
  header{padding:14px 18px;border-bottom:1px solid #1d2533;display:flex;align-items:center;gap:16px}
  h1{font-size:16px;margin:0;color:var(--acc);letter-spacing:.5px}
  .pill{background:#121826;border:1px solid #233047;border-radius:999px;padding:3px 10px;color:var(--mut)}
  main{padding:18px;display:grid;grid-template-columns:1fr 1fr;gap:16px}
  .card{background:#0f1420;border:1px solid #1d2533;border-radius:10px;padding:14px}
  .card h2{margin:0 0 10px;font-size:13px;color:var(--mut);text-transform:uppercase;letter-spacing:.6px}
  .chip{display:inline-block;margin:3px;padding:4px 9px;border-radius:7px;background:#142033;border:1px solid #25344c}
  .chip b{color:var(--acc)} .chip small{color:var(--mut)}
  table{width:100%;border-collapse:collapse} td,th{text-align:left;padding:4px 6px;border-bottom:1px solid #1a2230}
  .gauge{height:10px;border-radius:6px;background:linear-gradient(90deg,var(--warn),#ffe07a,var(--acc))}
  .gauge > i{display:block;height:100%;border-radius:6px;background:#0c0f14}
  .btns{margin-top:10px;display:flex;gap:8px}
  button{background:#15233a;color:var(--fg);border:1px solid #2a3a57;border-radius:8px;padding:7px 12px;cursor:pointer}
  button:hover{border-color:var(--acc)}
  pre{white-space:pre-wrap;color:var(--mut);max-height:160px;overflow:auto}
  a{color:var(--acc)}
</style>
<header>
  <h1>SLAUGHTERHOUSE5</h1><span class="pill" id=tick>tick 0</span>
  <span class="pill" id=weight>learned L4 weight 0.00</span>
  <span style="flex:1"></span>
  <span class="pill">local dashboard</span>
</header>
<main>
  <div class="card"><h2>Genome (taught lessons)</h2><div id=genome></div></div>
  <div class="card"><h2>Population (evolving)</h2><div id=pop></div></div>
  <div class="card"><h2>Learned L4 weight</h2>
    <div class="gauge"><i id=gfill></i></div>
    <pre id=vweight></pre>
    <div class="btns">
      <button onclick="run(10,false)">Run 10 ticks</button>
      <button onclick="run(10,true)">Reset &amp; run 10</button>
    </div>
  </div>
  <div class="card"><h2>Last differences / verdicts</h2>
    <pre id=diff></pre>
  </div>
</main>
<script>
function render(s){
  document.getElementById('tick').textContent='tick '+s.tick;
  document.getElementById('weight').textContent='learned L4 weight '+ (+s.learned_weight).toFixed(3);
  document.getElementById('gfill').style.width=(50+ (+s.learned_weight)*50)+'%';
  document.getElementById('vweight').textContent='weight = '+ (+s.learned_weight).toFixed(4)+'\n'
    +'differences logged: '+s.differences_ticks+' ticks\n'
    +'last differing pairs: '+JSON.stringify(s.last_differing_pairs);
  document.getElementById('genome').innerHTML = s.genome.slice(-12).map(g=>
    '<span class=chip><b>'+(g.toward||'?')+'</b> <small>deep:'+(g.deep||'-')
    +' ran:'+(g.ran)+' w:'+(g.weight||0).toFixed(2)+'</small></span>').join('');
  document.getElementById('pop').innerHTML = '<table><tr><th>name</th><th>plane</th>'
    +'<th>fit</th><th>gen</th></tr>'+s.population.map(p=>'<tr><td>'+p.name+'</td><td>'
    +p.plane+'</td><td>'+p.fitness+'</td><td>'+p.gen+'</td></tr>').join('')+'</table>';
  document.getElementById('diff').textContent='verdicts: '+s.verdicts.slice(-10).join(' ');
}
function tick(){fetch('/state').then(r=>r.json()).then(render).catch(()=>{});}
function run(n,reset){fetch('/run?n='+n+'&reset='+reset).then(()=>setTimeout(tick,400));}
setInterval(tick,2000); tick();
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
        if self.path.startswith("/state"):
            self._send(200, json.dumps(state_snapshot()))
        elif self.path.startswith("/run"):
            import urllib.parse as up
            q = up.parse_qs(up.urlparse(self.path).query)
            n = int(q.get("n", ["10"])[0])
            reset = q.get("reset", ["false"])[0] == "true"
            threading.Thread(target=run_pulse_bg, args=(n, reset), daemon=True).start()
            self._send(200, json.dumps({"ok": True, "n": n, "reset": reset}))
        elif self.path in ("/", "/index.html"):
            self._send(200, HTML, "text/html")
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def log_message(self, *a):
        pass


def main():
    import webbrowser
    srv = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Slaughterhouse5 dashboard  ->  http://127.0.0.1:{PORT}/")
    print("  triggers PULSE runs in-process; reads bios/state/ (git-versioned).")
    try:
        webbrowser.open(f"http://127.0.0.1:{PORT}/")
    except Exception:
        pass
    srv.serve_forever()


if __name__ == "__main__":
    main()
