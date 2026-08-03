"""BioSphere kernel — boots from the i4 seed and wires the organs.

The kernel is the ONLY thing that knows about all ten modules. Organs are
registered lazily and talked to through Capsules, never imported directly by
one another. This is the "cell membrane": it holds shared state and the tick,
and it is what makes the biosphere a single closed body rather than ten
islands.
"""
from __future__ import annotations

import hashlib
import os
import sys
from typing import Dict, Optional

from .contract import Capsule, CapsuleKind
from .state import StateStore
from cortex import zones as ZG

HERE = os.path.dirname(os.path.abspath(__file__))
SW = os.path.dirname(HERE)  # slaughterhouse5/
if SW not in sys.path:
    sys.path.insert(0, SW)

# canonical identity anchor (I-13 v2 FROZEN; == i4 / agent / subagent)
FROZEN_SPEC_SHA = "64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8"


class SealViolation(Exception):
    """Raised by BioSphere.emit when a capsule crosses a zone boundary without
    the sovereign's seal. The structure is SEALED: a non-L0 scope may not act
    across zones without cortex (S) authorizing it. 'A veto is a wall.'"""


def _zone_of(name: str) -> str:
    """Which zone a sender/receiver name belongs to (z1..z3, or 'bios' for the
    kernel/cortex itself). Used to decide whether a capsule needs the seal."""
    n = (name or "").lower()
    if n in ("bios", "cortex", "i4", "constructor", "jitonf"):
        return "z1"          # sovereign scope (L0)
    if n.startswith("agent"):
        return "z2"          # democratic sub-agents (L1)
    if n.startswith("subagent"):
        return "z3"          # stewardship sub-sub agents (L2)
    if n == "hermes":
        return "z1"          # Hermes is a special citizen admitted to the sovereign scope
    return "z2"             # default: treat unknown as democratic scope


class BioSphere:
    def __init__(self, state_dir: Optional[str] = None):
        self.state_dir = state_dir or os.path.join(HERE, "state")
        self.store = StateStore(self.state_dir)
        self.tick = 0
        self.trace_id = hashlib.sha256(FROZEN_SPEC_SHA.encode()).hexdigest()[:12]
        self.organs: Dict[str, object] = {}

    def register(self, name: str, mod) -> None:
        self.organs[name] = mod

    def emit(self, cap: Capsule) -> Capsule:
        cap.tick = self.tick
        cap.trace_id = self.trace_id
        # (sealed <->) : a capsule that crosses a zone boundary must carry the
        # sovereign's seal — UNLESS one endpoint is the sovereign scope (z1),
        # which is authorized by definition (cortex, the kernel, i4, Hermes act
        # for the sovereign and may reach any zone). Only a SUBORDINATE (z2/z3)
        # crossing into a DIFFERENT subordinate zone without a seal is refused.
        from_zone = _zone_of(cap.sender)
        to_zone = _zone_of(cap.receiver)
        if from_zone != to_zone and cap.kind not in (CapsuleKind.SEED, CapsuleKind.SENSE):
            if from_zone != "z1" and to_zone != "z1":
                payload = dict(cap.payload)
                seal = payload.pop("__seal__", None)
                if seal != ZG.seal(payload):
                    viol = SealViolation(
                        f"SEAL VIOLATION: {cap.sender}[{from_zone}] -> {cap.receiver}[{to_zone}] "
                        f"crosses a zone boundary without a valid sovereign seal (refused)")
                    self.store.append(Capsule("bios", "cortex", CapsuleKind.GOVERN_ZONES,
                                              {"sealed": True, "seal_ok": False, "violation": str(viol),
                                               "from": from_zone, "to": to_zone,
                                               "doctrine": ZG.DOCTRINE}))
                    raise viol
        self.store.append(cap)
        return cap

    def seed(self) -> object:
        """Boot from the i4 identity root (the planet's genesis)."""
        from i4 import i4_collapse
        c = i4_collapse(FROZEN_SPEC_SHA)
        self.emit(Capsule("bios", "i4", CapsuleKind.SEED,
                          {"root": c.root, "planes": len(c.per_plane)}))
        return c
