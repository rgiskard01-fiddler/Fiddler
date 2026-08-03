"""The PULSE — one metabolic tick: a PERSISTENT, EVOLVING multi-agent descent.

The population of agents is PERSISTED across ticks (state/population.json) and
EVOLVES: agents that lose the 2/3 arbitration are selected out and replaced by
genome-biased mutants (selection pressure toward consensus). Only the
arbitrated verdict is woven into the executed program.

seed(i4) -> emit(population, L1) -> host(subagents, L2) -> sense(L2)
-> compose(constructor, L3) -> arbitrate+log+EVOLVE(cortex, L4)
-> execute(jitonf, GATED by verdict) -> ingest.
"""
from __future__ import annotations

import importlib
import json
import os
from math import ceil
from collections import Counter

from .kernel import BioSphere, FROZEN_SPEC_SHA
from .contract import Capsule, CapsuleKind

POP = 3  # size of the persistent agent population


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
    return [
        {"name": "agent-0", "content": f"AGENT-A GENOME:{g}", "fitness": 0, "gen": 0},
        {"name": "agent-1", "content": f"AGENT-A GENOME:{g}", "fitness": 0, "gen": 0},
        {"name": "agent-2", "content": f"AGENT-B GENOME:{g}", "fitness": 0, "gen": 0},
    ]


def _evolve(pop, proposals, verdict, genome):
    """Selection: winners gain fitness; losing agents below zero are replaced
    by a genome-biased mutant (the biosphere nudges them toward consensus)."""
    g = ",".join(genome) or "none"
    for i, spec in enumerate(pop):
        if verdict and proposals[i] == verdict:
            spec["fitness"] += 1
        else:
            spec["fitness"] -= 1
        if spec["fitness"] < 0:
            spec["content"] = f"EVOLVE GENOME:{g}"
            spec["fitness"] = 0
            spec["gen"] += 1
    return pop


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

        # ---- L1 : emit the PERSISTENT population (agents keep their identity) ----
        agents = []
        for spec in pop:
            a = Agent.from_content(spec["name"], spec["content"].encode())
            agents.append(a)
            bio.emit(Capsule("bios", a.name, CapsuleKind.EMIT,
                             {"proposes": a.proposes_operant,
                              "fitness": spec["fitness"], "gen": spec["gen"],
                              "learned": a.learned_i13[:16] + "…"}))

        # ---- L2 SUBAGENT HOST : host each agent on the 18-bit plane ----
        for a in agents:
            sa = SubAgent.from_content(f"sa@{bio.tick}-{a.name}", a.attestation.encode(), l2_address=None)
            bio.emit(Capsule("bios", sa.name, CapsuleKind.EMIT,
                             {"l2_address": sa.l2_address, "host_symbol": sa.host_symbol}))

        # ---- L2 : cortex SENSE ----
        bio.emit(Capsule("bios", "cortex", CapsuleKind.SENSE,
                         {"L1": SENSE_L1, "L2": SENSE_L2}))

        # ---- L3 COMPOSE : (a) verified collapse over the whole population ----
        if c_root is None:
            c_root = i4_collapse(FROZEN_SPEC_SHA).root
        spheres = [Sphere(a.name, "agent", a.attestation) for a in agents]
        spheres += [Sphere("cortex", "cortex", json.dumps({"L1": SENSE_L1, "L2": SENSE_L2})),
                    Sphere("i4", "i4", c_root)]
        folds = build_fold(spheres)
        fold_ok, _ = verify_fold(folds[0]["seal"], folds[0]["proof"], folds[0]["root"])
        bio.emit(Capsule("bios", "constructor", CapsuleKind.FOLD,
                         {"verified": fold_ok, "root": folds[0]["root"][:16] + "…",
                          "spheres": len(spheres)}))

        # ---- L4 : cortex ARBITRATES + LOGS EVERY DIFFERENCE ----
        proposals = [a.proposes_operant for a in agents]
        verdict = arbitrate(proposals)
        diff_pairs = [[i, j] for i in range(len(agents)) for j in range(i + 1, len(agents))
                      if proposals[i] != proposals[j]]
        record = {
            "tick": bio.tick,
            "population": [{"name": a.name, "proposal": a.proposes_operant,
                            "fitness": spec["fitness"], "gen": spec["gen"]}
                           for a, spec in zip(agents, pop)],
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

        # ---- EVOLVE : selection pressure toward consensus (persisted) ----
        pop = _evolve(pop, proposals, verdict["verdict"], genome)
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
            gens = [s["gen"] for s in pop]
            print(f"[pulse {bio.tick}] {bio.store.summary()} | pop={proposals} "
                  f"verdict={verdict['verdict']} exec={ex['status']} "
                  f"fitness={fit} gen={gens} diffs={len(diff_pairs)} op={op_tag}")

    return bio


def main() -> None:
    bio = BioSphere()
    run_pulse(bio, n=10)


if __name__ == "__main__":
    main()
