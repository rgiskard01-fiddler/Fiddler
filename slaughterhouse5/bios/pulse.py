"""The PULSE — one metabolic tick of the biosphere.

Sequence (see BIOS-SPEC.md):
    seed(i4) -> emit(agent) -> govern(cortex+sense)
             -> fold(constructor) -> execute(jitonf) -> ingest -> loop

Every step is GENUINE:
  * i4 seeds the identity root
  * the agent attests the frozen spec and proposes an operant
  * cortex senses (feeds its own state back as features)
  * constructor BUILDS and VERIFIES a real Merkle collapse from the tick's
    material (agent attestation + cortex sense + i4 root)
  * jitonf EXECUTES real I-13 (the demo program)
  * the output is ingested as the next tick's material
"""
from __future__ import annotations

import importlib
import json
import os

from .kernel import BioSphere, FROZEN_SPEC_SHA
from .contract import Capsule, CapsuleKind


def _jitonf_demo_src() -> str:
    jf = importlib.import_module("jitonf")
    demo = os.path.join(os.path.dirname(jf.__file__), "examples", "demo.i13")
    src = open(demo, encoding="utf-8").read()
    # jitonf's lex does not consume '#' comment lines; strip them (full-line
    # or trailing) so the demo's comments don't break the lexer. The program
    # logic is unchanged.
    lines = []
    for ln in src.splitlines():
        if "#" in ln:
            ln = ln.split("#", 1)[0]
        if ln.strip():
            lines.append(ln)
    return "\n".join(lines)


def run_pulse(bio: BioSphere, n: int = 1, verbose: bool = True) -> BioSphere:
    for _ in range(n):
        bio.tick += 1

        # SEED — genesis from the i4 identity root (only first tick)
        c_root = None
        if bio.tick == 1:
            c = bio.seed()
            c_root = c.root

        # EMIT — an agent attests the frozen spec and proposes an operant
        from agent import Agent
        a = Agent.from_content(f"agent@{bio.tick}", f"pulse {bio.tick}".encode())
        bio.emit(Capsule("bios", "agent", CapsuleKind.EMIT,
                         {"proposes": a.proposes_operant,
                          "learned": a.learned_i13[:16] + "…"}))

        # SENSE — cortex feeds its own state back as features
        from cortex import SENSE_L1, SENSE_L2
        bio.emit(Capsule("bios", "cortex", CapsuleKind.SENSE,
                         {"L1": SENSE_L1, "L2": SENSE_L2}))

        # GOVERN + FOLD — constructor BUILDS and VERIFIES a real Merkle
        # collapse from this tick's material.
        from i4 import i4_collapse
        from constructor import build_fold, verify_fold, Sphere
        if c_root is None:
            c_root = i4_collapse(FROZEN_SPEC_SHA).root
        spheres = [
            Sphere(f"agent@{bio.tick}", "agent", a.attestation),
            Sphere("cortex", "cortex", json.dumps({"L1": SENSE_L1, "L2": SENSE_L2})),
            Sphere("i4", "i4", c_root),
        ]
        folds = build_fold(spheres)
        ok, computed = verify_fold(folds[0]["seal"], folds[0]["proof"], folds[0]["root"])
        bio.emit(Capsule("bios", "constructor", CapsuleKind.FOLD,
                         {"verified": ok,
                          "root": folds[0]["root"][:16] + "…",
                          "spheres": len(spheres)}))

        # EXECUTE — jitonf runs real I-13 (the demo program)
        from jitonf import run as jit_run
        res = jit_run(_jitonf_demo_src())
        bio.emit(Capsule("bios", "jitonf", CapsuleKind.EXECUTE,
                         {"sum": res["env"].get("sum"),
                          "r": res["env"].get("r"),
                          "steps": res["steps"]}))

        # INGEST — output becomes the next tick's material
        bio.emit(Capsule("bios", "bios", CapsuleKind.INGEST,
                         {"tick": bio.tick, "memory": bio.store.summary()}))

        if verbose:
            print(f"[pulse {bio.tick}] {bio.store.summary()} | "
                  f"exec sum={res['env'].get('sum')} r={res['env'].get('r')} "
                  f"steps={res['steps']} fold_ok={ok}")
    return bio


def main() -> None:
    bio = BioSphere()
    run_pulse(bio, n=3)


if __name__ == "__main__":
    main()
