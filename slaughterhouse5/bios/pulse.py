"""The PULSE — one metabolic tick of the biosphere.

Sequence (see BIOS-SPEC.md):
    seed(i4) -> emit(agent) -> govern(cortex+consensus)
             -> fold(constructor) -> execute(jitonf) -> ingest -> loop

This is the SHAPE. Each step calls the real organ where trivial; the deeper
execution wiring is filled in incrementally. Nothing here is simulated that
the modules can do for real.
"""
from __future__ import annotations

from .kernel import BioSphere
from .contract import Capsule, CapsuleKind


def run_pulse(bio: BioSphere, n: int = 1, verbose: bool = True) -> BioSphere:
    for _ in range(n):
        bio.tick += 1

        # SEED — only on the first tick (genesis from i4)
        if bio.tick == 1:
            bio.seed()

        # EMIT — an agent attests the frozen spec and proposes an operant
        from agent import Agent
        a = Agent.from_content(f"agent@{bio.tick}", f"pulse {bio.tick}".encode())
        bio.emit(Capsule("bios", "agent", CapsuleKind.EMIT,
                         {"proposes": a.proposes_operant, "learned": a.learned_i13}))

        # SENSE — cortex feeds its own state back as features
        from cortex import SENSE_L1, SENSE_L2
        bio.emit(Capsule("bios", "cortex", CapsuleKind.SENSE,
                         {"L1": SENSE_L1, "L2": SENSE_L2}))

        # GOVERN+FOLD — constructor records the attestation collapse
        # (the real Merkle verify is wired once a collapse is in state)
        bio.emit(Capsule("bios", "constructor", CapsuleKind.FOLD,
                         {"attested": a.learned_i13[:16] + "…"}))

        # EXECUTE — jitonf runs a minimal I-13 step (the execution hook)
        from jitonf import run as jit_run
        try:
            jit_run([{"x": bio.tick}, {"sum": "x + 7"}])
            status = "ran"
        except Exception as e:  # hook not yet fully wired -> record intent
            status = f"hook:{type(e).__name__}"
        bio.emit(Capsule("bios", "jitonf", CapsuleKind.EXECUTE, {"status": status}))

        # INGEST — output becomes the next tick's material
        bio.emit(Capsule("bios", "bios", CapsuleKind.INGEST,
                         {"tick": bio.tick, "memory": bio.store.summary()}))

        if verbose:
            print(f"[pulse {bio.tick}] {bio.store.summary()}")
    return bio


def main() -> None:
    bio = BioSphere()
    run_pulse(bio, n=3)


if __name__ == "__main__":
    main()
