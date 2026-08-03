"""The PULSE — one metabolic tick: a PERSISTENT, EVOLVING, MULTI-PLANE descent.

Roadmap now implemented:
  * L1 agents + L2 subagents independently propose; cortex ARBITRATES at 2/3.
  * Every difference is logged; minorities are fed a TEACH signal whose STRENGTH
    is set by the L4 deep-operand weight.
  * The taught lesson is persisted in the GENOME (remembered across runs).
  * The L4 deep-operand RESOLVER selects what executes (a wall).
  * The cortex's trained L4 weight folds into the run AND is a LEARNED parameter
    (state/learned_weight.json) that sharpens across ticks.
  * FUSE: ALL adopted operants are woven into ONE program (the running language
    accumulates several extensions at once) -- each operant is a REAL jitonf form
    (jitonf.operants.lower).
  * Agents INGEST prior capsules (self-reference of the biosphere's own output).
  * RESUME: state persists; --continue keeps the biosphere alive across runs.
"""
from __future__ import annotations

import importlib
import json
import os
from math import ceil

from .kernel import BioSphere, FROZEN_SPEC_SHA
from .contract import Capsule, CapsuleKind

POP = 3  # proposers per plane (so 2*POP = 6 total, 2/3 = 4 needed)

jitonf = importlib.import_module("jitonf")
jit_run = jitonf.run
jit_lower = jitonf.lower


# --------------------------------------------------------------------------
# persistence helpers (git-friendly, under bios/state/)
# --------------------------------------------------------------------------
def _p(bio, name):
    return os.path.join(bio.state_dir, name)


def _load(bio, name, default):
    pp = _p(bio, name)
    if not os.path.isfile(pp):
        return default
    try:
        return json.load(open(pp, encoding="utf-8"))
    except Exception:
        return default


def _save(bio, name, data):
    os.makedirs(bio.state_dir, exist_ok=True)
    json.dump(data, open(_p(bio, name), "w", encoding="utf-8"), indent=2)


def _seed_population(g):
    pop = []
    for i in range(POP):
        tag = "A" if i < POP - 1 else "B"
        pop.append({"name": f"agent-{i}", "plane": "L1",
                    "content": f"AGENT-{tag} GENOME:{g}", "fitness": 0, "gen": 0})
    for i in range(POP):
        tag = "A" if i < POP - 1 else "B"
        pop.append({"name": f"subagent-{i}", "plane": "L2",
                    "content": f"SUB-{tag} GENOME:{g}", "fitness": 0, "gen": 0})
    return pop


def _weighted_gjoin(genome):
    """Join genome 'toward' operants, repeating each by its L4 weight magnitude
    so a strongly-weighted deep selection dominates the bias fed back into
    future seeding/evolution."""
    parts = []
    for d in genome:
        toward = d.get("toward", "")
        if not toward:
            continue
        w = d.get("weight", 1.0) or 0.0
        k = max(1, int(round(abs(w) * 3)))
        parts.append(",".join([toward] * k))
    return ",".join(parts) or "none"


def _prior_gist(bio):
    """(C) Agents INGEST prior capsules: a gist of the last INGEST capsule is
    folded into agent content -> the biosphere self-references its own output."""
    cd = os.path.join(bio.state_dir, "capsules")
    if not os.path.isdir(cd):
        return ""
    last = None
    for f in sorted(os.listdir(cd)):
        if not f.endswith(".json"):
            continue
        try:
            c = json.load(open(os.path.join(cd, f), encoding="utf-8"))
        except Exception:
            continue
        if c.get("kind") == "INGEST":
            last = c
    if not last:
        return ""
    pl = last.get("payload", {})
    return f"PRIOR:{pl.get('memory','')}|{'/'.join(pl.get('genome', [])[:2])}"


def _teach(content, verdict, strength=1.0):
    """Teach signal. L4 trained weight scales `strength` -> the teach reach:
    weak cortex signal searches fewer candidates (soft teach); strong -> full."""
    from agent import Agent
    base = content if " TEACH:" in content else content + " TEACH:"
    cap = max(1, int(4096 * strength))
    for k in range(cap):
        cand = f"{base}{k}"
        if Agent.from_content("taught", cand.encode()).proposes_operant == verdict:
            return cand
    return content


def _evolve(members, verdict, genome, deep_weight=None):
    """Selection across BOTH planes. L4 weight MODULATES the teach strength."""
    g = genome or "none"
    strength = abs(deep_weight) if deep_weight is not None else 0.0
    for spec, prop in members:
        if verdict and prop == verdict:
            spec["fitness"] += 1
        else:
            spec["fitness"] = max(0, spec["fitness"] - 1)
            if verdict and strength >= 0.15:
                spec["content"] = _teach(spec["content"], verdict, strength)
                spec["gen"] += 1
            else:
                spec["content"] = f"EVOLVE GENOME:{g}"
                spec["gen"] += 1
    return members


def _compose_fused_program(operants):
    """(B) FUSE: weave ALL adopted operants into one program. Each keyword is a
    REAL jitonf operant form; jitonf.lower() expands it to core I-13."""
    lines = []
    for op in operants:
        lines.append(f'I __operant__ <- "{op}" ;')
        lines.append(f"{op} ;")          # native operant form -> lowered by jitonf
    return "\n".join(lines) + "\n"


def _write_viewer(bio):
    """(G) Live PULSE viewer: a static HTML snapshot of the biosphere's state."""
    data = {
        "genome": _load(bio, "learned.json", []),
        "differences_ticks": len(_load(bio, "differences.json", [])),
        "population": _load(bio, "population.json", []),
        "learned_weight": _load(bio, "learned_weight.json", 0.6),
        "ledger": bio.store.summary(),
    }
    html = ("<!doctype html><meta charset=utf-8><title>Slaughterhouse5 — PULSE viewer</title>"
            "<h1>Slaughterhouse5 biosphere — live PULSE</h1>"
            f"<pre>{json.dumps(data, indent=1)}</pre>"
            "<p>Generated by bios.pulse — the biosphere's own trace.</p>")
    for path in (_p(bio, "pulse-view.html"),
                 os.path.join(os.path.dirname(os.path.dirname(bio.state_dir)), "pulse-view.html")):
        try:
            open(path, "w", encoding="utf-8").write(html)
        except Exception:
            pass


def run_pulse(bio: BioSphere, n: int = 1, verbose: bool = True, reset: bool = False) -> BioSphere:
    from agent import Agent
    from subagent import SubAgent
    from cortex import SENSE_L1, SENSE_L2, arbitrate, resolve, L4_ADDR_MAX, CortexBoundary
    from i4 import i4_collapse
    from constructor import build_fold, verify_fold, Sphere

    if reset:
        import shutil
        cd = os.path.join(bio.state_dir, "capsules")
        if os.path.isdir(cd):
            shutil.rmtree(cd)
        os.makedirs(cd, exist_ok=True)

    genome = _load(bio, "learned.json", [])
    diff_log = _load(bio, "differences.json", [])
    pop = _load(bio, "population.json", None)
    lw = _load(bio, "learned_weight.json", 0.6)
    if pop is None:
        g_join = _weighted_gjoin(genome)
        pop = _seed_population(g_join)
        _save(bio, "population.json", pop)

    for _ in range(n):
        bio.tick += 1
        c_root = None
        if bio.tick == 1:
            c = bio.seed()
            c_root = c.root

        # (C) prior capsules ingested into agent content
        prior = _prior_gist(bio)
        agents_spec = [s for s in pop if s["plane"] == "L1"]
        sub_specs = [s for s in pop if s["plane"] == "L2"]
        agents = [Agent.from_content(s["name"], (s["content"] + " " + prior).encode()) for s in agents_spec]
        subagents = [SubAgent.from_content(s["name"], (s["content"] + " " + prior).encode(), l2_address=None)
                     for s in sub_specs]
        for a in agents:
            bio.emit(Capsule("bios", a.name, CapsuleKind.EMIT,
                             {"plane": "L1", "proposes": a.proposes_operant,
                              "fitness": next(s["fitness"] for s in agents_spec if s["name"] == a.name),
                              "learned": a.learned_i13[:16] + "…"}))
        for sa in subagents:
            bio.emit(Capsule("bios", sa.name, CapsuleKind.EMIT,
                             {"plane": "L2", "proposes": sa.proposes_operant,
                              "l2_address": sa.l2_address, "host_symbol": sa.host_symbol}))

        bio.emit(Capsule("bios", "cortex", CapsuleKind.SENSE, {"L1": SENSE_L1, "L2": SENSE_L2}))

        if c_root is None:
            c_root = i4_collapse(FROZEN_SPEC_SHA).root
        spheres = ([Sphere(a.name, "agent", a.attestation) for a in agents]
                   + [Sphere(sa.name, "subagent", sa.attestation) for sa in subagents]
                   + [Sphere("cortex", "cortex", json.dumps({"L1": SENSE_L1, "L2": SENSE_L2})),
                      Sphere("i4", "i4", c_root)])
        folds = build_fold(spheres)
        fold_ok, _ = verify_fold(folds[0]["seal"], folds[0]["proof"], folds[0]["root"])
        bio.emit(Capsule("bios", "constructor", CapsuleKind.FOLD,
                         {"verified": fold_ok, "root": folds[0]["root"][:16] + "…", "spheres": len(spheres)}))

        # ---- L4 ARBITRATE L1+L2 ----
        members = ([(s, a.proposes_operant) for s, a in zip(agents_spec, agents)]
                   + [(s, sa.proposes_operant) for s, sa in zip(sub_specs, subagents)])
        proposals = [p for _, p in members]
        verdict = arbitrate(proposals)
        diff_pairs = [[i, j] for i in range(len(members)) for j in range(i + 1, len(members))
                      if proposals[i] != proposals[j]]
        taught_names = [s["name"] for s, p in members if verdict["verdict"] and p != verdict["verdict"]]
        if verdict["verdict"]:
            genome.append({"toward": verdict["verdict"], "taught": taught_names, "tick": bio.tick})
            _save(bio, "learned.json", genome)
        record = {
            "tick": bio.tick,
            "population": [{"name": s["name"], "plane": s["plane"], "proposal": p,
                            "fitness": s["fitness"], "gen": s["gen"]} for s, p in members],
            "distinct": verdict["distinct"], "counts": verdict["counts"],
            "differing_pairs": diff_pairs, "taught": taught_names,
            "verdict": verdict["verdict"], "reason": verdict["reason"],
        }
        diff_log.append(record)
        _save(bio, "differences.json", diff_log)
        bio.emit(Capsule("bios", "cortex", CapsuleKind.GOVERN,
                         {"population": proposals, "distinct": verdict["distinct"],
                          "differing_pairs": diff_pairs, "taught": taught_names,
                          "verdict": verdict["verdict"], "reason": verdict["reason"]}))

        # (B) FUSE all adopted operants into one program
        adopted = sorted({d["toward"] for d in genome if d.get("toward")}
                        | ({verdict["verdict"]} if verdict["verdict"] else set()))

        # ---- L4 DEEP-OPERAND RESOLVER : SELECTS what executes (wall) ----
        candidates = verdict["distinct"] or ([verdict["verdict"]] if verdict["verdict"] else [])
        l4_addr = int(agents[0].content_sha256, 16) % (L4_ADDR_MAX + 1)
        try:
            operand = resolve(l4_addr)
            op_tag = getattr(operand, "tag", "?")
            deep_op = candidates[operand.addr % len(candidates)] if candidates else None
            cortex_weight = operand.weight
        except CortexBoundary:
            op_tag = "void"
            deep_op = None
            cortex_weight = None
        bio.emit(Capsule("bios", "cortex", CapsuleKind.SENSE,
                         {"l4_resolve": l4_addr, "operand": op_tag,
                          "deep_selected": deep_op, "weight": cortex_weight}))

        # ---- EXECUTE : fuse + run only the deep-resolved == ratified operants ----
        if deep_op is not None and deep_op == verdict["verdict"] and adopted:
            program = jit_lower(_compose_fused_program(adopted))
            bio.emit(Capsule("bios", "constructor", CapsuleKind.COMPOSE,
                             {"operants": adopted, "program": program, "l4_weight": lw}))
            res = jit_run(program)
            ex = {"status": "ran", "operants": adopted,
                  "results": {k: v for k, v in res["env"].items() if k.startswith("result_")},
                  "l4_weight": round(lw, 4), "steps": res["steps"]}
            genome.append({"toward": deep_op, "taught": taught_names, "tick": bio.tick,
                           "deep": deep_op, "ran": True, "weight": round(lw, 4)})
            _save(bio, "learned.json", genome)
        else:
            reason = (f"L4 deep-operand selected {deep_op}, not the ratified {verdict['verdict']}"
                      if deep_op is not None else "L4 address void (cortex boundary)")
            ex = {"status": "VETOED", "reason": reason}
            if deep_op is not None:
                genome.append({"toward": verdict["verdict"], "taught": taught_names,
                               "tick": bio.tick, "deep": deep_op, "ran": False, "weight": round(lw, 4)})
                _save(bio, "learned.json", genome)
        bio.emit(Capsule("bios", "jitonf", CapsuleKind.EXECUTE, ex))

        # (E) L4 weight is a LEARNED parameter: nudge toward agreement
        if deep_op is not None and deep_op == verdict["verdict"]:
            lw = max(-1.0, min(1.0, lw * 0.9 + 0.1))
        else:
            lw = max(-1.0, min(1.0, lw * 0.9 - 0.1))
        _save(bio, "learned_weight.json", lw)

        # ---- EVOLVE : L4-weighted teach feeds differences back ----
        g_join = _weighted_gjoin(genome)
        members = _evolve(members, verdict["verdict"], g_join, lw)
        _save(bio, "population.json", pop)

        bio.emit(Capsule("bios", "bios", CapsuleKind.INGEST,
                         {"tick": bio.tick, "memory": bio.store.summary(), "genome": genome}))

        if verbose:
            print(f"[pulse {bio.tick}] {bio.store.summary()} | L1={[a.proposes_operant for a in agents]} "
                  f"L2={[sa.proposes_operant for sa in subagents]} verdict={verdict['verdict']} "
                  f"deep={deep_op} fuse={adopted} lw={round(lw,3)} exec={ex['status']} diffs={len(diff_pairs)}")

    _write_viewer(bio)
    return bio


def main() -> None:
    import sys
    reset = "--reset" in sys.argv
    run_pulse(BioSphere(), n=10, reset=reset)


if __name__ == "__main__":
    main()
