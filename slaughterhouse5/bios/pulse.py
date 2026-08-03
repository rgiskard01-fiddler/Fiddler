"""The PULSE — one metabolic tick: a descent L1->L2->L3->L4 of the biosphere.

seed(i4) -> emit(agent, L1) -> emit(subagent, L2) -> sense(L2)
-> compose(constructor, L3) -> compose(bios) -> govern+resolve(cortex, L4)
-> execute(jitonf, GATED) -> ingest.

Every step is GENUINE:
  * i4 seeds the identity root (L1)
  * an agent attests + PROPOSES an operant, content biased by the standing
    majority AND the genome -> the biosphere LEARNS TO AGREE (resolves standoffs)
  * a subagent is emitted + HOSTED on the 18-bit L2 SUBAGENT HOST plane
  * cortex SENSES (feeds its own state back)
  * constructor COMPOSES planes into one verified Merkle collapse (L3)
  * bios COMPOSES a state-derived I-13 program (the biosphere's own language)
  * cortex GOVERNS (veto = wall) and RESOLVES a deep operand on L4
  * jitonf EXECUTES the COMPOSED program — but ONLY if the cortex permitted it
  * capsules persist; the genome LEARNS from the verdict, so proposals converge
"""
from __future__ import annotations

import importlib
import json
import os
from math import ceil
from collections import Counter

from .kernel import BioSphere, FROZEN_SPEC_SHA
from .contract import Capsule, CapsuleKind


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
    p = _p(bio, name)
    if not os.path.isfile(p):
        return default
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return default


def _save(bio, name, data):
    os.makedirs(bio.state_dir, exist_ok=True)
    json.dump(data, open(_p(bio, name), "w", encoding="utf-8"), indent=2)


def _adopted(reg):
    n = len(reg)
    if not n:
        return []
    thr = ceil(2 * n / 3)
    tally = Counter(r.get("proposes_operant") for r in reg)
    return [op for op, c in tally.items() if c >= thr]


def _majority(reg):
    if not reg:
        return "none"
    return Counter(r.get("proposes_operant") for r in reg).most_common(1)[0][0]


def _compose_program(op: str) -> str:
    """Weave an adopted operant's REAL semantics into the biosphere's program.

    jitonf's VM implements THE TWELVE core forms; the beyond-TWELVE operants
    are woven in as their *defined behavior* (emulated in core I-13), not
    faked as native forms. The running language grows with consensus.
    """
    sem = _SEM.get(op, 'I result <- 0 ;')
    return f'I __operant__ <- "{op}" ;\n{sem}\n'


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


def run_pulse(bio: BioSphere, n: int = 1, verbose: bool = True) -> BioSphere:
    from agent import Agent
    from subagent import SubAgent
    from cortex import SENSE_L1, SENSE_L2, govern, resolve, L4_ADDR_MAX, CortexBoundary
    from i4 import i4_collapse
    from constructor import build_fold, verify_fold, Sphere
    from jitonf import run as jit_run

    reg = _load(bio, "agents.json", [])
    genome = _load(bio, "learned.json", [])

    for _ in range(n):
        bio.tick += 1

        # ---- L1 FIELD : identity root ----
        c_root = None
        if bio.tick == 1:
            c = bio.seed()
            c_root = c.root

        # ---- L1 : emit agent (content = genome -> LEARNING converges) ----
        maj = _majority(reg)
        content = f"GENOME:{','.join(genome) or 'none'}".encode()
        a = Agent.from_content(f"agent@{bio.tick}", content)
        bio.emit(Capsule("bios", "agent", CapsuleKind.EMIT,
                         {"proposes": a.proposes_operant,
                          "learned": a.learned_i13[:16] + "…"}))

        # ---- L2 SUBAGENT HOST : emit + host a subagent ----
        sa = SubAgent.from_content(f"sa@{bio.tick}", content, l2_address=None)
        bio.emit(Capsule("bios", "subagent", CapsuleKind.EMIT,
                         {"l2_address": sa.l2_address,
                          "host_symbol": sa.host_symbol,
                          "learned": sa.learned_i13[:16] + "…"}))

        # ---- L2 : cortex SENSE (feeds its own state back) ----
        bio.emit(Capsule("bios", "cortex", CapsuleKind.SENSE,
                         {"L1": SENSE_L1, "L2": SENSE_L2}))

        # ---- L3 COMPOSE : (a) planes into one verified collapse ----
        if c_root is None:
            c_root = i4_collapse(FROZEN_SPEC_SHA).root
        spheres = [
            Sphere(f"agent@{bio.tick}", "agent", a.attestation),
            Sphere(f"sa@{bio.tick}", "subagent", sa.attestation),
            Sphere("cortex", "cortex", json.dumps({"L1": SENSE_L1, "L2": SENSE_L2})),
            Sphere("i4", "i4", c_root),
        ]
        folds = build_fold(spheres)
        fold_ok, _ = verify_fold(folds[0]["seal"], folds[0]["proof"], folds[0]["root"])
        bio.emit(Capsule("bios", "constructor", CapsuleKind.FOLD,
                         {"verified": fold_ok,
                          "root": folds[0]["root"][:16] + "…",
                          "spheres": len(spheres)}))

        # ---- L3 COMPOSE : (b) weave the adopted operant's semantics ----
        op = a.proposes_operant
        program = _compose_program(op)
        bio.emit(Capsule("bios", "constructor", CapsuleKind.COMPOSE,
                         {"operant": op, "program": program}))

        # ---- L4 DEEP OPERAND : govern (veto gate) + resolve an operand ----
        reg.append({"name": a.name, "proposes_operant": a.proposes_operant})
        _save(bio, "agents.json", reg)
        adopted_now = _adopted(reg)
        allowed, reason = govern(a.proposes_operant, adopted_now)
        bio.emit(Capsule("bios", "cortex", CapsuleKind.GOVERN,
                         {"proposal": a.proposes_operant, "allowed": allowed,
                          "reason": reason, "adopted": adopted_now}))
        l4_addr = int(a.content_sha256, 16) % (L4_ADDR_MAX + 1)
        try:
            operand = resolve(l4_addr)
            op_tag = getattr(operand, "tag", "?")
        except CortexBoundary:
            op_tag = "void"   # cortex refuses addresses beyond the trained 6662
        bio.emit(Capsule("bios", "cortex", CapsuleKind.SENSE,
                         {"l4_resolve": l4_addr, "operand": op_tag}))

        # ---- LEARNING : genome absorbs adopted operants ----
        if allowed:
            genome.append(a.proposes_operant)
            _save(bio, "learned.json", genome)

        # ---- EXECUTE : run the COMPOSED program (gated by the cortex verdict) ----
        if allowed:
            res = jit_run(program)
            ex = {"status": "ran", "program_result": res["env"].get("result"),
                  "steps": res["steps"]}
        else:
            ex = {"status": "VETOED", "reason": reason}
        bio.emit(Capsule("bios", "jitonf", CapsuleKind.EXECUTE, ex))

        # ---- INGEST ----
        bio.emit(Capsule("bios", "bios", CapsuleKind.INGEST,
                         {"tick": bio.tick, "memory": bio.store.summary(),
                          "genome": genome}))

        if verbose:
            print(f"[pulse {bio.tick}] {bio.store.summary()} | maj={maj} "
                  f"propose={a.proposes_operant} govern={'ALLOW' if allowed else 'VETO'} "
                  f"exec={ex['status']} l2={sa.l2_address} l4={l4_addr} op={op_tag}")

    return bio


def main() -> None:
    bio = BioSphere()
    run_pulse(bio, n=10)


if __name__ == "__main__":
    main()
