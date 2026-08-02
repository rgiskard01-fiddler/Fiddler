"""The PULSE — one metabolic tick: a descent L1->L2->L3->L4 of the biosphere.

seed(i4) -> emit(agent, L1) -> emit(subagent, L2) -> sense(L2)
-> compose(constructor, L3) -> govern+resolve(cortex, L4)
-> execute(jitonf, GATED) -> ingest.

Every step is GENUINE:
  * i4 seeds the identity root (L1)
  * an agent attests + PROPOSES an operant, content shaped by the genome
  * a subagent is emitted + HOSTED on the 18-bit L2 SUBAGENT HOST plane
  * cortex SENSES (feeds its own state back)
  * constructor COMPOSES the planes into one verified Merkle collapse (L3)
  * cortex GOVERNS (veto = wall) and RESOLVES a deep operand on L4
  * jitonf EXECUTES real I-13 — but ONLY if the cortex permitted it
  * capsules persist; the genome LEARNS from the verdict, so proposals converge
"""
from __future__ import annotations

import importlib
import json
import os
from math import ceil

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
    tally = {}
    for r in reg:
        op = r.get("proposes_operant")
        tally[op] = tally.get(op, 0) + 1
    return [op for op, c in tally.items() if c >= thr]


def run_pulse(bio: BioSphere, n: int = 1, verbose: bool = True) -> BioSphere:
    from agent import Agent
    from subagent import SubAgent
    from cortex import SENSE_L1, SENSE_L2, govern, resolve, L4_ADDR_MAX
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

        # ---- L1 : emit agent (content shaped by genome -> LEARNING) ----
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

        # ---- L3 COMPOSE : planes composed into one verified collapse ----
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

        # ---- L4 DEEP OPERAND : govern (veto gate) + resolve an operand ----
        reg.append({"name": a.name, "proposes_operant": a.proposes_operant})
        _save(bio, "agents.json", reg)
        adopted = _adopted(reg)
        allowed, reason = govern(a.proposes_operant, adopted)
        bio.emit(Capsule("bios", "cortex", CapsuleKind.GOVERN,
                         {"proposal": a.proposes_operant, "allowed": allowed,
                          "reason": reason, "adopted": adopted}))
        l4_addr = int(a.content_sha256, 16) % (L4_ADDR_MAX + 1)
        operand = resolve(l4_addr)
        bio.emit(Capsule("bios", "cortex", CapsuleKind.SENSE,
                         {"l4_resolve": l4_addr,
                          "operand": getattr(operand, "tag", "?")}))

        # ---- LEARNING : genome absorbs adopted operants ----
        if allowed:
            genome.append(a.proposes_operant)
            _save(bio, "learned.json", genome)

        # ---- EXECUTE (gated by the cortex verdict) ----
        if allowed:
            res = jit_run(_jitonf_demo_src())
            ex = {"status": "ran", "sum": res["env"].get("sum"),
                  "r": res["env"].get("r"), "steps": res["steps"]}
        else:
            ex = {"status": "VETOED", "reason": reason}
        bio.emit(Capsule("bios", "jitonf", CapsuleKind.EXECUTE, ex))

        # ---- INGEST ----
        bio.emit(Capsule("bios", "bios", CapsuleKind.INGEST,
                         {"tick": bio.tick, "memory": bio.store.summary(),
                          "genome": genome}))

        if verbose:
            print(f"[pulse {bio.tick}] {bio.store.summary()} | "
                  f"propose={a.proposes_operant} govern={'ALLOW' if allowed else 'VETO'} "
                  f"exec={ex['status']} l2={sa.l2_address} l4={l4_addr} op={getattr(operand,'tag','?')}")

    return bio


def main() -> None:
    bio = BioSphere()
    run_pulse(bio, n=8)


if __name__ == "__main__":
    main()
