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

HERE = os.path.dirname(os.path.abspath(__file__))
SW = os.path.dirname(HERE)  # slaughterhouse5/
if SW not in sys.path:
    sys.path.insert(0, SW)

# canonical identity anchor (I-13 v2 FROZEN; == i4 / agent / subagent)
FROZEN_SPEC_SHA = "64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8"


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
        self.store.append(cap)
        return cap

    def seed(self) -> object:
        """Boot from the i4 identity root (the planet's genesis)."""
        from i4 import i4_collapse
        c = i4_collapse(FROZEN_SPEC_SHA)
        self.emit(Capsule("bios", "i4", CapsuleKind.SEED,
                          {"root": c.root, "planes": len(c.per_plane)}))
        return c
