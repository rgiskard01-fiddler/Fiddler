"""Capsule — the only message organs exchange.

Organs never import each other; they pass Capsules through the bios kernel.
This is what lets the biosphere compose the modules while each organ stays
independently "cuttable" (I-13 design).
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict


class CapsuleKind(str, Enum):
    SEED = "seed"
    EMIT = "emit"
    GOVERN = "govern"
    GOVERN_ZONES = "govern_zones"
    FOLD = "fold"
    COMPOSE = "compose"
    EXECUTE = "execute"
    INGEST = "ingest"
    SENSE = "sense"


@dataclass
class Capsule:
    sender: str
    receiver: str
    kind: CapsuleKind
    payload: Dict[str, Any] = field(default_factory=dict)
    tick: int = 0
    trace_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["kind"] = self.kind.value
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Capsule":
        d = dict(d)
        d["kind"] = CapsuleKind(d["kind"])
        return cls(**d)
