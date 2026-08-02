"""The PULSE — one metabolic tick of the biosphere.

seed(i4) -> emit(agent) -> sense(cortex) -> govern(cortex)
         -> fold(constructor) -> execute(jitonf, gated by govern) -> ingest -> loop

Every step is GENUINE:
  * i4 seeds the identity root
  * the agent attests the frozen spec and PROPOSES an operant
  * cortex SENSES (feeds its own state back) and GOVERNS (vetoes what is not a
    core form nor adopted by consensus -- the veto is a wall)
  * constructor BUILDS and VERIFIES a real Merkle collapse from the tick's
    material
  * jitonf EXECUTES real I-13 -- but ONLY if the cortex permitted it
  * the output is ingested, and the agent registry ACCUMULATES, so consensus
    (and therefore what may run) evolves across ticks. The biosphere becomes
    genuinely self-regulating: it interacts with itself only.
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
    lines = []
    for ln in src.splitlines():
        if "#" in ln:
            ln = ln.split("#", 1)[0]
        if ln.strip():
            lines.append(ln)
    return "\n".join(lines)


def _registry_path(bio) -> str:
    return os.path.join(bio.state_dir, "agents.json")


def _load_registry(bio):
    p = _registry_path(bio)
    if not os.path.isfile(p):
        return []
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return []


def _save_registry(bio, reg) -> None:
    os.makedirs(bio.state_dir, exist_ok=True)
    json.dump(reg, open(_registry_path(bio), "w", encoding="utf-8"), indent=2)


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
    from cortex import SENSE_L1, SENSE_L2, govern
    from i4 import i4_collapse
    from constructor import build_fold, verify_fold, Sphere
    from jitonf import run as jit_run

    reg = _load_registry(bio)

    for _ in range(n):
        bio.tick += 1

        # SEED
        c_root = None
        if bio.tick == 1:
            c = bio.seed()
            c_root = c.root

        # EMIT — agent attests + proposes an operant
        a = Agent.from_content(f"agent@{bio.tick}", f"pulse {bio.tick}".encode())
        bio.emit(Capsule("bios", "agent", CapsuleKind.EMIT,
                         {"proposes": a.proposes_operant,
                          "learned": a.learned_i13[:16] + "…"}))

        # SENSE — cortex feeds its own state back as features
        bio.emit(Capsule("bios", "cortex", CapsuleKind.SENSE,
                         {"L1": SENSE_L1, "L2": SENSE_L2}))

        # GOVERN + FOLD — constructor builds + verifies a real collapse
        if c_root is None:
            c_root = i4_collapse(FROZEN_SPEC_SHA).root
        spheres = [
            Sphere(f"agent@{bio.tick}", "agent", a.attestation),
            Sphere("cortex", "cortex", json.dumps({"L1": SENSE_L1, "L2": SENSE_L2})),
            Sphere("i4", "i4", c_root),
        ]
        folds = build_fold(spheres)
        fold_ok, _ = verify_fold(folds[0]["seal"], folds[0]["proof"], folds[0]["root"])
        bio.emit(Capsule("bios", "constructor", CapsuleKind.FOLD,
                         {"verified": fold_ok, "root": folds[0]["root"][:16] + "…",
                          "spheres": len(spheres)}))

        # GOVERN — cortex gates what may execute (veto = wall)
        reg.append({"name": a.name, "proposes_operant": a.proposes_operant})
        _save_registry(bio, reg)
        adopted = _adopted(reg)
        allowed, reason = govern(a.proposes_operant, adopted)
        bio.emit(Capsule("bios", "cortex", CapsuleKind.GOVERN,
                         {"proposal": a.proposes_operant, "allowed": allowed,
                          "reason": reason, "adopted": adopted}))

        # EXECUTE — jitonf runs real I-13 ONLY if the cortex permitted it
        if allowed:
            res = jit_run(_jitonf_demo_src())
            exec_payload = {"status": "ran", "sum": res["env"].get("sum"),
                            "r": res["env"].get("r"), "steps": res["steps"]}
        else:
            exec_payload = {"status": "VETOED", "reason": reason}
        bio.emit(Capsule("bios", "jitonf", CapsuleKind.EXECUTE, exec_payload))

        # INGEST — output becomes the next tick's material
        bio.emit(Capsule("bios", "bios", CapsuleKind.INGEST,
                         {"tick": bio.tick, "memory": bio.store.summary()}))

        if verbose:
            print(f"[pulse {bio.tick}] {bio.store.summary()} | "
                  f"propose={a.proposes_operant} govern={'ALLOW' if allowed else 'VETO'} "
                  f"exec={exec_payload['status']}")
    return bio


def main() -> None:
    bio = BioSphere()
    run_pulse(bio, n=5)


if __name__ == "__main__":
    main()
