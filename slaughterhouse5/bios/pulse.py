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
    g = genome if isinstance(genome, str) else ",".join(d.get("toward", "") for d in genome) or "none"
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


def _teach(content, verdict):
    """Teach signal: find a content perturbation such that the agent's OWN
    propose_operant yields the ratified verdict. The minority agent is not
    bypassed -- it is taught an input that makes its own logic agree
    (genuine teach, not a forced override)."""
    from agent import Agent
    base = content if " TEACH:" in content else content + " TEACH:"
    for k in range(4096):
        cand = f"{base}{k}"
        if Agent.from_content("taught", cand.encode()).proposes_operant == verdict:
            return cand
    return content


def _evolve(members, verdict, genome):
    """Selection across BOTH planes. Winners gain fitness. Losers are fed a
    TEACH signal: their content is nudged (via their own proposal function)
    toward the ratified verdict, so the population CONVERGES instead of merely
    being logged as different. With no verdict, they reseed as mutants."""
    g = genome or "none"   # genome param is the joined "toward" string (genome memory)
    for spec, prop in members:
        if verdict and prop == verdict:
            spec["fitness"] += 1
        else:
            spec["fitness"] = max(0, spec["fitness"] - 1)
            if verdict:
                spec["content"] = _teach(spec["content"], verdict)
                spec["gen"] += 1
            else:
                spec["content"] = f"EVOLVE GENOME:{g}"
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


def _weighted_gjoin(genome):
    """Join the genome's 'toward' operants, repeating each by its trained L4
    weight magnitude so a strongly-weighted deep selection dominates the bias
    fed back into future seeding/evolution."""
    parts = []
    for d in genome:
        toward = d.get("toward", "")
        if not toward:
            continue
        w = d.get("weight", 1.0) or 0.0
        k = max(1, int(round(abs(w) * 3)))
        parts.append(",".join([toward] * k))
    return ",".join(parts) or "none"


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
        g_join = _weighted_gjoin(genome)
        pop = _seed_population(g_join)
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
        taught_names = [s["name"] for s, p in members if verdict["verdict"] and p != verdict["verdict"]]
        # THE TAUGHT LESSON IS PERSISTED AS PART OF THE GENOME (remembered across ticks/runs)
        if verdict["verdict"]:
            genome.append({"toward": verdict["verdict"], "taught": taught_names, "tick": bio.tick})
            _save(bio, "learned.json", genome)
        record = {
            "tick": bio.tick,
            "population": [{"name": s["name"], "plane": s["plane"], "proposal": p,
                            "fitness": s["fitness"], "gen": s["gen"]}
                           for s, p in members],
            "distinct": verdict["distinct"], "counts": verdict["counts"],
            "differing_pairs": diff_pairs,
            "taught": taught_names,
            "verdict": verdict["verdict"], "reason": verdict["reason"],
        }
        diff_log.append(record)
        _save(bio, "differences.json", diff_log)
        bio.emit(Capsule("bios", "cortex", CapsuleKind.GOVERN,
                         {"population": proposals, "distinct": verdict["distinct"],
                          "differing_pairs": diff_pairs,
                          "taught": taught_names,
                          "verdict": verdict["verdict"], "reason": verdict["reason"]}))

        # ---- EVOLVE : teach signal feeds differences back; genome biases future ----
        g_join = _weighted_gjoin(genome)
        members = _evolve(members, verdict["verdict"], g_join)
        _save(bio, "population.json", pop)

        # ---- L3 COMPOSE : (b) weave the ratified operant's semantics (staged) ----
        ratified = verdict["verdict"]
        program = None

        # ---- L4 DEEP-OPERAND RESOLVER : SELECTS which operant executes ----
        # The cortex resolves a 13-bit deep operand; its address selects one of
        # the population's distinct proposals. L4 is a WALL: only when the
        # deep-resolved operant IS the 2/3 ratified verdict may it run.
        candidates = verdict["distinct"] or ([ratified] if ratified else [])
        l4_addr = int(agents[0].content_sha256, 16) % (L4_ADDR_MAX + 1)
        try:
            operand = resolve(l4_addr)
            op_tag = getattr(operand, "tag", "?")
            deep_op = candidates[operand.addr % len(candidates)] if candidates else None
            deep_weight = operand.weight
        except CortexBoundary:
            op_tag = "void"
            deep_op = None
            deep_weight = None
        bio.emit(Capsule("bios", "cortex", CapsuleKind.SENSE,
                         {"l4_resolve": l4_addr, "operand": op_tag,
                          "deep_selected": deep_op, "weight": deep_weight}))

        # ---- EXECUTE : run only the deep-resolved + ratified operant ----
        # L4 SELECTION FEEDBACK: the deep-resolved choice is written into the
        # genome so it is remembered and reinforced across ticks/runs.
        if deep_op is not None and deep_op == ratified:
            w_int = int(round((deep_weight + 1) * 2)) if deep_weight is not None else 0
            program = (_compose_program(deep_op)
                       + f"I w <- {w_int} ;\nI weighted_result <- result + w ;\n")
            bio.emit(Capsule("bios", "constructor", CapsuleKind.COMPOSE,
                             {"operant": deep_op, "program": program, "l4_weight": deep_weight}))
            res = jit_run(program)
            ex = {"status": "ran", "operant": deep_op,
                  "program_result": res["env"].get("weighted_result"),
                  "l4_weight": round(deep_weight, 4) if deep_weight is not None else None,
                  "steps": res["steps"]}
            genome.append({"toward": deep_op, "taught": taught_names,
                           "tick": bio.tick, "deep": deep_op, "ran": True,
                           "weight": round(deep_weight, 4) if deep_weight is not None else 0.0})
            _save(bio, "learned.json", genome)
        else:
            reason = (f"L4 deep-operand selected {deep_op}, not the ratified {ratified}"
                      if deep_op is not None else "L4 address void (cortex boundary)")
            ex = {"status": "VETOED", "reason": reason}
            if deep_op is not None:   # negative feedback: rejected selection not reinforced
                genome.append({"toward": ratified, "taught": taught_names,
                               "tick": bio.tick, "deep": deep_op, "ran": False,
                               "weight": round(deep_weight, 4) if deep_weight is not None else 0.0})
                _save(bio, "learned.json", genome)
        bio.emit(Capsule("bios", "jitonf", CapsuleKind.EXECUTE, ex))

        # ---- INGEST ----
        bio.emit(Capsule("bios", "bios", CapsuleKind.INGEST,
                         {"tick": bio.tick, "memory": bio.store.summary(),
                          "genome": genome}))

        if verbose:
            fit = [s["fitness"] for s in pop]
            print(f"[pulse {bio.tick}] {bio.store.summary()} | L1={[a.proposes_operant for a in agents]} "
                  f"L2={[sa.proposes_operant for sa in subagents]} verdict={verdict['verdict']} "
                  f"deep={deep_op} exec={ex['status']} diffs={len(diff_pairs)} op={op_tag}")

    return bio


def main() -> None:
    bio = BioSphere()
    run_pulse(bio, n=10)


if __name__ == "__main__":
    main()
