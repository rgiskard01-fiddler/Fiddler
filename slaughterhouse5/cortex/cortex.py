"""
cortex
======

The L4 **DEEP OPERAND** plane and the *governor + sensor* of the I-13
four-plane stack.

Grounded in ``I,Robot/hermes.i13`` (unified baseline, merged v1->v2->v3):

    L1 FIELD        : 395162 nodes / 19 bits
    L2 SUBAGENT HOST: 209068 nodes / 18 bits
    L3 COMPOSE      :  38742 nodes / 16 bits
    L4 DEEP OPERAND:   6662 nodes / 13 bits   <- cortex-only

The cortex is the only scope that may touch L4.  Its job, in the spec's
own words:

    "a feature is advice, a veto is a wall"
    "the cortex still verifies at the end"

So cortex provides two things:

  * GOVERNOR  - the five parameter-free rules applied as a hard wall
                (veto, -I, depth, idempotence, address).
  * SENSOR    - its own state fed back as input features (v1#arch:
                L2 mismatch 15.0->0.6, L1 stray-close 65.0->1.0).

The 6662 L4 *operand payloads* are learned weights and are NOT present
as text in the corpus.  ``Cortex`` therefore builds a deterministic
stand-in operand table over the real 13-bit address space so the
resolver, boundaries, and governance are exercised exactly as specified;
the payloads are clearly marked as a reproducible placeholder pending
the trained weights.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# --------------------------------------------------------------------------
# the four-plane stack (verbatim from hermes.i13)
# --------------------------------------------------------------------------
PLANES: Dict[str, dict] = {
    "L1": {"name": "FIELD",         "nodes": 395162, "bits": 19},
    "L2": {"name": "SUBAGENT HOST", "nodes": 209068, "bits": 18},
    "L3": {"name": "COMPOSE",       "nodes":  38742, "bits": 16},
    "L4": {"name": "DEEP OPERAND",  "nodes":   6662, "bits": 13},
}
PLANE_ORDER = ("L1", "L2", "L3", "L4")
L4_NODES = PLANES["L4"]["nodes"]          # 6662
L4_BITS = PLANES["L4"]["bits"]            # 13
L4_ADDR_MAX = (1 << L4_BITS) - 1          # 8191 (13-bit space)

# rule_reach : reach per 1,000 nodes, across L1..L4 (hermes.i13 rule_reach)
RULE_REACH: Dict[str, List[float]] = {
    "veto":        [137.5, 52.4, 56.2, 53.4],
    "-I":          [137.5, 52.4, 56.2, 53.4],
    "depth":       [168.5, 212.5, 182.1, 187.1],
    "idempotence": [59.0, 0.0, 0.0, 0.0],
    "address":     [168.5, 0.0, 0.0, 0.0],
}
# idempotence & address are 0.0 above L1 (no statements inside an expression).

# cortex sensor feedback (real empirical deltas cited in v1#arch / v1#base)
SENSE_L1: Tuple[float, ...] = (65.0, 1.0, 33.8, 16.6, 40.0)   # stray-close, mismatch, clean...
SENSE_L2: Tuple[float, ...] = (15.0, 0.6, 79.6, 80.6, 0.0, 40.0)

VETO_MSG = "a feature is advice, a veto is a wall"


# --------------------------------------------------------------------------
# L4 deep-operand table (deterministic stand-in over the real address space)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Operand:
    addr: int
    tag: str
    weight: float          # stand-in for a trained L4 weight, in [-1, 1]


def _standin_weight(addr: int) -> float:
    h = hashlib.sha256(f"L4:{addr}".encode()).digest()
    return (int.from_bytes(h[:8], "big") / (2 ** 64 - 1)) * 2.0 - 1.0


def _standin_tag(addr: int) -> str:
    h = hashlib.sha256(f"tag:{addr}".encode()).hexdigest()
    return "DOP-" + h[:8]


class CortexBoundary(Exception):
    """Raised when a non-L4 scope tries to touch a deep operand."""


def build_operand_table(n: int = L4_NODES) -> List[Operand]:
    """Deterministic stand-in L4 operand table (n entries, 13-bit addrs)."""
    return [Operand(a, _standin_tag(a), _standin_weight(a)) for a in range(n)]


# --------------------------------------------------------------------------
# the cortex: governor + sensor
# --------------------------------------------------------------------------
@dataclass
class Cortex:
    operands: List[Operand] = field(default_factory=build_operand_table)
    scope: str = "L4"                       # cortex lives at the deep plane

    # -- resolver (cortex-only) -------------------------------------------
    def resolve(self, addr: int) -> Operand:
        """Resolve a deep operand by 13-bit address. Cortex-only: addresses
        outside the trained 6662 are 'void' (the cortex refuses them)."""
        if not isinstance(addr, int) or addr < 0:
            raise CortexBoundary(f"negative address {addr} is not an L4 operand")
        if addr >= len(self.operands):
            raise CortexBoundary(
                f"address {addr} is void (L4 holds {len(self.operands)} trained operands)")
        return self.operands[addr]

    def can_reach(self, addr: int) -> bool:
        try:
            self.resolve(addr); return True
        except CortexBoundary:
            return False

    # -- governor: the five parameter-free rules --------------------------
    @staticmethod
    def veto(open_stack: List[str], closer: str, expect: Dict[str, str]) -> Tuple[bool, str]:
        """RULE veto: forbid the wrong closer.

        ``open_stack`` = open constructs (most-recent last); ``expect`` maps
        an opener -> its required closer.  Returns (allowed, reason)."""
        if not open_stack:
            return False, "no open construct to close"
        top = open_stack[-1]
        owed = expect.get(top)
        if owed is None:
            return False, f"opener {top!r} has no defined closer"
        if closer != owed:
            return False, f"veto: {closer!r} is the wrong closer for {top!r} (owe {owed!r})"
        return True, "closer matches"

    @staticmethod
    def supply_owed(openers: List[str], expect: Dict[str, str]) -> List[str]:
        """RULE -I: supply the owed closers for any still-open constructs."""
        owed = []
        for op in reversed(openers):
            c = expect.get(op)
            if c:
                owed.append(c)
        return owed

    @staticmethod
    def refuse_if_paid(open_planes: List[str], new_plane: str) -> Tuple[bool, str]:
        """RULE depth: refuse a plane already paid for (already open)."""
        if new_plane in open_planes:
            return True, f"depth: plane {new_plane} already open -> refuse"
        return False, "depth: ok"

    @staticmethod
    def idempotent(before: str, after: str) -> bool:
        """RULE idempotence: a no-op cannot repeat (I am I)."""
        return before == after

    @staticmethod
    def write_address(counter: int) -> int:
        """RULE address: the substrate writes the position (13-bit masked)."""
        return counter & L4_ADDR_MAX

    # -- sensor -----------------------------------------------------------
    def sense(self) -> dict:
        """The cortex feeding its own state back as input features."""
        return {
            "L1": list(SENSE_L1),
            "L2": list(SENSE_L2),
            "note": "L2 mismatch 15.0->0.6 ; L1 stray-close 65.0->1.0 (v1#arch)",
        }

    # -- governance verification ------------------------------------------
    def verify(self, trace: List[dict]) -> Tuple[bool, List[str]]:
        """Verify a governance trace.  Each event is either
            {"kind": "feature", ...}            # advice only, never enforced
            {"kind": "veto", "open": [...], "closer": str, "expect": {...}}
        A veto whose closer mismatches is a *wall* violation -> fail."""
        report: List[str] = []
        ok = True
        for i, ev in enumerate(trace):
            if ev.get("kind") == "feature":
                report.append(f"[{i}] feature (advice, not enforced)")
            elif ev.get("kind") == "veto":
                allowed, why = self.veto(ev.get("open", []),
                                         ev.get("closer", ""),
                                         ev.get("expect", {}))
                if not allowed:
                    ok = False
                    report.append(f"[{i}] VETO WALL VIOLATION: {why}")
                else:
                    report.append(f"[{i}] veto ok: {why}")
            else:
                report.append(f"[{i}] unknown event {ev.get('kind')!r}")
        return ok, report

    # -- bridge: cortex governance as an I-13 ATTRIBUTE data collapse -----
    def to_i13_policy(self) -> dict:
        """Serialize cortex governance as an I-13 ATTRIBUTE data collapse
        (data only; sha256 is not an IVM-13-S opcode, so governance is
        performed here and handed to jitonf as data)."""
        return {
            "ATTRIBUTE": {
                "module": "cortex",
                "scope": self.scope,
                "planes": {k: {"nodes": v["nodes"], "bits": v["bits"]} for k, v in PLANES.items()},
                "rules": list(RULE_REACH.keys()),
                "rule_reach": RULE_REACH,
                "l4_operands": len(self.operands),
                "l4_bits": L4_BITS,
                "doctrine": VETO_MSG,
            }
        }
