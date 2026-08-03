"""The PULSE — one metabolic tick: a PERSISTENT, EVOLVING, MULTI-PLANE descent.

Two proposing populations, on two planes, arbitrated together:
  * L1 agents   (agent.Attest)        -> propose
  * L2 subagents (subagent.SubAgent)   -> INDEPENDENTLY propose on the 18-bit
                                          SUBAGENT HOST plane
The cortex ARBITRATES the combined population at >= 2/3; EVERY difference is
logged; losers are selected out and replaced by genome-biased mutants. Only the
arbitrated verdict is woven into the executed program.

seed(i4) -> emit(L1+L2, propose) -> sense(L2) -> compose(L3)
-> arbitrate+log+EVOLVE(cortex, L4) -> execute(jitonf, gated) -> ingest.
"""
from __future__ import annotations

import importlib
import json
import os
from math import ceil
from collections import Counter

from .kernel import BioSphere, FROZEN_SPEC_SHA
from .contract import Capsule, CapsuleKind

POP = 3  # proposers per plane (so 2*POP = 6 total, 2/3 = 4 needed)


def _jitonf_demo_src() -> str:
    jf = importlib.import_module("jitonf")
    demo = os.path.join(os.path.dirname(jf.__file__), "examples", "demo.i13")
    src = open(demo, encoding="utf-8").read()
    out = []
    for ln in src.splitlines():
        if "#" in ln:
            ln = ln.split("#", 1)[0]
        if ln.strip():
            out.append(ln)
    return "\n".join(out)


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


def _seed_population(genome):
    g = ",".join(genome) or "none"
    pop = []
    for i in range(POP):
        tag = "A" if i < POP - 1 else "B"   # 2/3 majority per plane
        pop.append({"name": f"agent-{i}", "plane": "L1",
                    "content": f"AGENT-{tag} GENOME:{g}", "fitness": 0, "gen": 0})
    for i in range(POP):
        tag = "A" if i < POP - 1 else "B"
        pop.append({"name": f"subagent-{i}", "plane": "L2",
                    "content": f"SUB-{tag} GENOME:{g}", "fitness": 0, "gen": 0})
    return pop


def _evolve(members, verdict, genome):
    """Selection across BOTH planes: winners gain fitness; losing specs below
    zero are replaced by a genome-biased mutant (nudged toward consensus)."""
    g = ",".join(genome) or "none"
    for spec, prop in members:
        if verdict and prop == verdict:
            spec["fitness"] += 1
        else:
            spec["fitness"] -= 1
        if spec["fitness"] < 0:
            spec["content"] = f"EVOLVE GENOME:{g}"
            spec["fitness"] = 0
            spec["gen"] += 1
    return members


# Each adopted operant's real semantics, emulated in executable core I-13.
_SEM = {
    "IMPORT": 'I m <- "mod" ; I ok <- 1 ; I result <- ok ;',
    "LOOP":   'I acc <- 0 ; acc <- acc + 1 ; acc <- acc + 1 ; acc <- acc + 1 ; I result <- acc ;',
    "LAMBDA": 'def lam(I a) { -> a + 1 ; } I result <- lam(4) ;',
    "MATCH":  'I v <- 2 ; I m <- 0 ; if (v < 3) { m <- 1 ; } else { m <- 0 ; } I result <- m ;',
    "TRY":    'I ok <- 1 ; I safe <- 0 ; if (ok < 1) { safe <- 0 ; } else { safe <- 1 ; } I result <- safe ;',
    "YIELD":  'I state <- 0 ; I y <- state + 1 ; I result <- y ;',
    "SPAWN":  'I p1 <- 3 + 4 ; I p2 <- 5 + 5 ; I result <- p1 + p2 ;',
    "CAST":   'I n <- 7 ; I c <- n ; I result <- c ;',
    "INDEX":  'I a0 <- 10 ; I a1 <- 20 ; I idx <- 1 ; I v <- 0 ; if (idx < 1) { v <- a0 ; } else { v <- a1 ; } I result <- v ;',
    "SLICE":  'I lo <- 0 ; I x <- 1 ; I hi <- 2 ; I ins <- 0 ; if (x < hi) { if (lo < x) { ins <- 1 ; } else { ins <- 0 ; } } else { ins <- 0 ; } I result <- ins ;',
    "ASSERT": 'I cond <- 1 ; I flag <- 0 ; if (cond < 1) { flag <- 0 ; } else { flag <- 1 ; } I result <- flag ;',
    "AWAIT":  'I ready <- 1 ; I val <- 0 ; if (ready < 1) { val <- 0 ; } else { val <- 42 ; } I result <- val ;',
}


def _compose_program(op: str) -> str:
    """Weave an adopted operant's REAL semantics into the biosphere's program."""
    sem = _SEM.get(op, 'I result <- 0 ;')
    return f'I __operant__ <- "{op}" ;\n{sem}\n'


def run_pulse(bio: BioSphere, n: int = 1, verbose: bool = True) -> BioSphere:
    from agent import Agent
    from subagent import SubAgent
    from cortex import SENSE_L1, SENSE_L2, arbitrate, resolve, L4_ADDR_MAX, CortexBoundary
    from i4 import i4_collapse
    from constructor import build_fold, verify_fold, Sphere
    from jitonf import run as jit_run

    genome = _load(bio, "learned.json", [])
    diff_log = _load(bio, "differences.json", [])
    pop = _load(bio, "population.json", None)
    if pop is None:
        pop = _seed_population(genome)
        _save(bio, "population.json", pop)

    for _ in range(n):
        bio.tick += 1

        # ---- L1 FIELD : identity root ----
        c_root = None
        if bio.tick == 1:
            c = bio.seed()
            c_root = c.root

        # ---- L1 + L2 : emit BOTH proposing populations (persisted identity) ----
        agents_spec = [s for s in pop if s["plane"] == "L1"]
        sub_specs = [s for s in pop if s["plane"] == "L2"]
        agents = [Agent.from_content(s["name"], s["content"].encode()) for s in agents_spec]
        subagents = [SubAgent.from_content(s["name"], s["content"].encode(), l2_address=None)
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

        # ---- L2 : cortex SENSE ----
        bio.emit(Capsule("bios", "cortex", CapsuleKind.SENSE,
                         {"L1": SENSE_L1, "L2": SENSE_L2}))

        # ---- L3 COMPOSE : (a) verified collapse over BOTH planes ----
        if c_root is None:
            c_root = i4_collapse(FROZEN_SPEC_SHA).root
        spheres = ([Sphere(a.name, "agent", a.attestation) for a in agents]
                   + [Sphere(sa.name, "subagent", sa.attestation) for sa in subagents]
                   + [Sphere("cortex", "cortex", json.dumps({"L1": SENSE_L1, "L2": SENSE_L2})),
                      Sphere("i4", "i4", c_root)])
        folds = build_fold(spheres)
        fold_ok, _ = verify_fold(folds[0]["seal"], folds[0]["proof"], folds[0]["root"])
        bio.emit(Capsule("bios", "constructor", CapsuleKind.FOLD,
                         {"verified": fold_ok, "root": folds[0]["root"][:16] + "…",
                          "spheres": len(spheres)}))

        # ---- L4 : cortex ARBITRATES L1+L2 (logs EVERY difference) ----
        members = ([(s, a.proposes_operant) for s, a in zip(agents_spec, agents)]
                   + [(s, sa.proposes_operant) for s, sa in zip(sub_specs, subagents)])
        proposals = [p for _, p in members]
        verdict = arbitrate(proposals)
        diff_pairs = [[i, j] for i in range(len(members)) for j in range(i + 1, len(members))
                      if proposals[i] != proposals[j]]
        record = {
            "tick": bio.tick,
            "population": [{"name": s["name"], "plane": s["plane"], "proposal": p,
                            "fitness": s["fitness"], "gen": s["gen"]}
                           for s, p in members],
            "distinct": verdict["distinct"], "counts": verdict["counts"],
            "differing_pairs": diff_pairs, "verdict": verdict["verdict"],
            "reason": verdict["reason"],
        }
        diff_log.append(record)
        _save(bio, "differences.json", diff_log)
        bio.emit(Capsule("bios", "cortex", CapsuleKind.GOVERN,
                         {"population": proposals, "distinct": verdict["distinct"],
                          "differing_pairs": diff_pairs, "verdict": verdict["verdict"],
                          "reason": verdict["reason"]}))

        # ---- EVOLVE : selection pressure across BOTH planes (persisted) ----
        members = _evolve(members, verdict["verdict"], genome)
        _save(bio, "population.json", pop)

        # ---- L3 COMPOSE : (b) weave the arbitrated operant's semantics ----
        program = None
        if verdict["verdict"]:
            program = _compose_program(verdict["verdict"])
            bio.emit(Capsule("bios", "constructor", CapsuleKind.COMPOSE,
                             {"operant": verdict["verdict"], "program": program}))

        # ---- L4 : resolve a deep operand (void = real cortex boundary) ----
        l4_addr = int(agents[0].content_sha256, 16) % (L4_ADDR_MAX + 1)
        try:
            operand = resolve(l4_addr)
            op_tag = getattr(operand, "tag", "?")
        except CortexBoundary:
            op_tag = "void"
        bio.emit(Capsule("bios", "cortex", CapsuleKind.SENSE,
                         {"l4_resolve": l4_addr, "operand": op_tag}))

        # ---- EXECUTE : run the arbitrated program (gated by the verdict) ----
        if verdict["verdict"]:
            res = jit_run(program)
            ex = {"status": "ran", "operant": verdict["verdict"],
                  "program_result": res["env"].get("result"), "steps": res["steps"]}
            genome.append(verdict["verdict"])
            _save(bio, "learned.json", genome)
        else:
            ex = {"status": "VETOED", "reason": verdict["reason"]}
        bio.emit(Capsule("bios", "jitonf", CapsuleKind.EXECUTE, ex))

        # ---- INGEST ----
        bio.emit(Capsule("bios", "bios", CapsuleKind.INGEST,
                         {"tick": bio.tick, "memory": bio.store.summary(),
                          "genome": genome}))

        if verbose:
            fit = [s["fitness"] for s in pop]
            print(f"[pulse {bio.tick}] {bio.store.summary()} | L1={[a.proposes_operant for a in agents]} "
                  f"L2={[sa.proposes_operant for sa in subagents]} verdict={verdict['verdict']} "
                  f"exec={ex['status']} diffs={len(diff_pairs)} op={op_tag}")

    return bio


def main() -> None:
    bio = BioSphere()
    run_pulse(bio, n=10)


if __name__ == "__main__":
    main()
