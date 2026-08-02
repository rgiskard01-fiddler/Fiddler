"""
i4  (I^4)
====

The **I-symbol to the 4th** -- the I-collapse across all four planes, and
the self-referential deep-operand root of the I-13 program.

Grounded in the user's module scaffold and ``I,Robot/hermes.i13``:

  * The learning scope is {i, c, sa, ssa}; ``i`` is the ROOT element.
  * The topology root is ``-+[[-{ i^4 , c (cortex), agent , subagent } ...``
  * i4 = "the I-symbol to the 4th (I^4): the I-collapse across all four
    planes; the self-referential deep-operand root."
  * The 13th alphabet symbol is ``I`` (identity / self-reference); the
    idempotence rule is "a no-op cannot repeat (I am I)".
  * The frozen spec sha and the 6-agent .dlw consensus root are the
    declared IDENTITY that every downstream agent attests to.

So i4 is the **identity anchor**:

  * IDENTITY   - ``I(x) = x`` (idempotent self-reference) and "I am I".
  * I^4 COLLAPSE - the same identity asserted at each of L1..L4, folded
                 (hex-string concat, consistent with constructor) into a
                 single self-referential root across the four planes.
  * ATTEST     - attest that a claimed spec sha equals the frozen identity.

The fold uses the same hex-string concatenation convention as the
``constructor`` module (discovered by matching the sealed corpus folds),
so i4's collapse is a first-class citizen of the same collapse format.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List, Tuple

# --------------------------------------------------------------------------
# real identity anchors (verbatim from I,Robot/hermes.i13)
# --------------------------------------------------------------------------
FROZEN_SPEC_SHA = "64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8"
CONSENSUS_ROOT = "cd4593338104cd9ff0b4ae39ff95b22b74649c1d532b8d7d35ef7120c12455c8"
CONSENSUS_AGENTS = 6

# the four-plane stack (verbatim from hermes.i13)
PLANES: Tuple[Tuple[str, str, int], ...] = (
    ("L1", "FIELD", 395162),
    ("L2", "SUBAGENT HOST", 209068),
    ("L3", "COMPOSE", 38742),
    ("L4", "DEEP OPERAND", 6662),
)
I_SYMBOL = "I"          # the 13th symbol: identity / self-reference
N_SYMBOLS = 13


def h(s: str) -> str:
    """sha256 of a hex-or-text string (encoded to bytes)."""
    if isinstance(s, str):
        s = s.encode("utf-8")
    return hashlib.sha256(s).hexdigest()


def fold2(a: str, b: str) -> str:
    """Binary fold step -- hex-string concat, matching the corpus convention."""
    return h(a + b)


PAD = "0" * 64   # sparse-tree padding leaf for partial collapses


def merkle_fold(digests: List[str]) -> str:
    """Balanced binary Merkle fold over an arbitrary list of digests,
    padding to a power of two with PAD.  Hex-string concat throughout."""
    if not digests:
        raise ValueError("merkle_fold needs at least one digest")
    n = len(digests)
    size = 1
    while size < n:
        size *= 2
    layer = list(digests) + [PAD] * (size - n)
    while len(layer) > 1:
        nxt = [fold2(layer[i], layer[i + 1]) for i in range(0, len(layer), 2)]
        layer = nxt
    return layer[0]


# --------------------------------------------------------------------------
# the identity root
# --------------------------------------------------------------------------
def identity(x):
    """The I operation: return the self unchanged. I(x) = x."""
    return x


def i_am_i(x) -> bool:
    """The idempotence rule at the identity level: I(I(x)) == I(x)."""
    return identity(identity(x)) == identity(x)


@dataclass
class I4Collapse:
    seed: str
    per_plane: List[Dict[str, str]]
    root: str

    def as_dict(self) -> dict:
        return {"seed": self.seed, "per_plane": self.per_plane, "root": self.root}


def i4_collapse(seed: str = FROZEN_SPEC_SHA) -> I4Collapse:
    """
    The I-collapse across all four planes.

    For each plane, bind the identity seed to that plane:
        pdigest = h(seed + plane_name + str(nodes))
    Then fold the four plane digests (balanced binary Merkle, hex concat)
    into a single self-referential root -- I^4.

    Each plane contributes: dropping any plane changes the root.
    """
    pdigests = []
    per_plane = []
    for label, name, nodes in PLANES:
        pd = h(seed + name + str(nodes))
        pdigests.append(pd)
        per_plane.append({"plane": label, "name": name, "digest": pd})
    root = merkle_fold(pdigests)
    return I4Collapse(seed=seed, per_plane=per_plane, root=root)


def attest(claimed_sha: str, frozen: str = FROZEN_SPEC_SHA) -> bool:
    """Attest that a claimed spec sha equals the frozen I-13 identity.

    This is the exact check every downstream agent (agent/subagent) performs
    to bind itself to the same declared identity of I-13 v2."""
    return claimed_sha == frozen


def self_consistent(model: dict) -> bool:
    """'I am I': a self-model whose self-reference is consistent with its id."""
    return model.get("self") == model.get("id")


# --------------------------------------------------------------------------
# bridge: i4 identity as an I-13 ATTRIBUTE data collapse
# --------------------------------------------------------------------------
def to_i13_identity(collapse: I4Collapse = None) -> dict:
    collapse = collapse or i4_collapse()
    return {
        "ATTRIBUTE": {
            "module": "i4",
            "symbol": I_SYMBOL,
            "symbol_index": N_SYMBOLS,
            "doctrine": "I am I",
            "frozen_spec_sha": FROZEN_SPEC_SHA,
            "consensus_root": CONSENSUS_ROOT,
            "consensus_agents": CONSENSUS_AGENTS,
            "planes": [{"plane": p[0], "name": p[1], "nodes": p[2]} for p in PLANES],
            "i4_root": collapse.root,
        }
    }
