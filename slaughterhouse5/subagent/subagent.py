"""
subagent
========

The **L2 SUBAGENT HOST** plane (18-bit, trained, 66) -- the hosted learner.

From the baseline (I,Robot/hermes.i13) the plane stack is
    L1 FIELD 395162/19 · L2 SUBAGENT HOST 209068/18 · L3 COMPOSE 38742/16
    · L4 DEEP OPERAND 6662/13
and the learning scope is {i, c, sa, ssa}; ``sa`` is the subagent.

A subagent is an agent (it ATTESTS the frozen I-13 spec and PROPOSES a
deterministic operant beyond THE TWELVE -- see the agent module), *plus* a
HOSTING layer: it is bound to an 18-bit L2 host address (0..209067) within
the L2 SUBAGENT HOST plane, whose trained alphabet has 66 symbols.

This module is deliberately self-contained (it re-declares the shared
consensus primitives) so it can be "cut" independently, exactly as the
I-13 design intends. Its behaviour mirrors ``agent``; the hosting layer
is what makes it ``sa`` rather than a bare ``agent``.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List, Tuple

# --------------------------------------------------------------------------
# the L2 SUBAGENT HOST plane (verbatim from the baseline)
# --------------------------------------------------------------------------
L2_NODES = 209068
L2_BITS = 18
L2_ADDR_MAX = (1 << L2_BITS) - 1            # 262143 (18-bit space)
HOST_ALPHABET_SIZE = 66                     # trained L2 host alphabet

# canonical identity anchor (I-13 v2 FROZEN; == agent / i4)
FROZEN_SPEC_SHA = "64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8"

THE_TWELVE = ["NAME", "CONSTANT", "ATTRIBUTE", "CALL", "ASSIGN", "ARG",
              "EXPR", "IF", "COMPARE", "FUNCTIONDEF", "RETURN", "BINOP"]
OPERANT_POOL: List[Tuple[str, str, str]] = [
    ("LOOP",   "iteration",            "Ada Lovelace / Goldstine-von Neumann (the loop)"),
    ("LAMBDA", "anonymous function",   "Alonzo Church (lambda calculus, 1936)"),
    ("MATCH",  "pattern match",        "Robin Milner (ML, 1973)"),
    ("TRY",    "exception handling",   "John Goodenough (1975)"),
    ("YIELD",  "generator / coroutine","Barbara Liskov (CLU, 1975)"),
    ("IMPORT", "module reference",     "Niklaus Wirth (Modula, 1975)"),
    ("SPAWN",  "concurrent process",   "C. A. R. Hoare (CSP, 1978)"),
    ("CAST",   "type coercion",        "Strachey / the typed lambda tradition"),
    ("INDEX",  "subscript access",     "Kenneth Iverson (APL, 1962)"),
    ("SLICE",  "range selection",      "van Rossum (Python) / Iverson lineage"),
    ("ASSERT", "invariant check",      "Alan Turing / Floyd-Hoare (assertions)"),
    ("AWAIT",  "asynchronous suspend", "the async/await lineage (Meijer et al.)"),
]

# The L2 host alphabet: 66 symbols. The first 25 are the real I-symbols
# (THE_TWELVE + "I") plus the 12 candidate operants; the remainder are
# deterministic host glyphs standing in for the trained L2 weights (which
# are not stored as text in the corpus).
def _build_host_alphabet() -> List[str]:
    base = list(THE_TWELVE) + ["I"] + [op[0] for op in OPERANT_POOL]
    out = list(base)
    i = 0
    while len(out) < HOST_ALPHABET_SIZE:
        out.append(f"H{i:02d}")           # deterministic host glyph stand-in
        i += 1
    return out[:HOST_ALPHABET_SIZE]

HOST_ALPHABET = _build_host_alphabet()


def sha256_hex(data) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def propose_operant(content_sha: str) -> Tuple[str, str, str]:
    name, kind, attr = OPERANT_POOL[int(content_sha, 16) % len(OPERANT_POOL)]
    assert name not in THE_TWELVE
    return name, kind, attr


def merkle(leaves: List[str]) -> str:
    if not leaves:
        return sha256_hex(b"empty")
    cur = list(leaves)
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur), 2):
            a = cur[i]
            b = cur[i + 1] if i + 1 < len(cur) else cur[i]
            nxt.append(sha256_hex(a + b))
        cur = nxt
    return cur[0]


@dataclass
class SubAgent:
    name: str
    content_sha256: str
    learned_i13: str
    proposes_operant: str
    operant_kind: str
    attribution: str
    l2_address: int
    host_symbol: str
    attestation: str = ""
    attestation_sha256: str = ""

    @classmethod
    def from_content(cls, name: str, content: bytes,
                     l2_address: int = None, frozen: str = FROZEN_SPEC_SHA) -> "SubAgent":
        csha = sha256_hex(content)
        op_name, op_kind, op_attr = propose_operant(csha)
        # hosting: bind to an 18-bit L2 address (derived if not given)
        if l2_address is None:
            l2_address = int(csha, 16) % (L2_ADDR_MAX + 1)
        else:
            if not (0 <= l2_address <= L2_ADDR_MAX):
                raise ValueError(f"L2 address {l2_address} out of 18-bit range")
        host_symbol = HOST_ALPHABET[int(csha, 16) % HOST_ALPHABET_SIZE]
        attestation = ("{name}|content:{csha}|learned:{frozen}|proposes:{op}|"
                       "host:L2@{addr}:{sym}").format(
            name=name, csha=csha, frozen=frozen, op=op_name,
            addr=l2_address, sym=host_symbol)
        return cls(
            name=name, content_sha256=csha, learned_i13=frozen,
            proposes_operant=op_name, operant_kind=op_kind, attribution=op_attr,
            l2_address=l2_address, host_symbol=host_symbol,
            attestation=attestation,
            attestation_sha256=sha256_hex(attestation.encode("utf-8")),
        )

    def verify_host(self) -> Tuple[bool, str]:
        """The cortex-style boundary check: is this subagent legitimately
        hosted on L2?"""
        if not (0 <= self.l2_address <= L2_ADDR_MAX):
            return False, f"L2 address {self.l2_address} out of 18-bit range"
        if self.host_symbol not in HOST_ALPHABET:
            return False, f"host symbol {self.host_symbol} not in L2 alphabet"
        if self.learned_i13 != FROZEN_SPEC_SHA:
            return False, "does not attest the frozen I-13 spec"
        return True, "hosted on L2 SUBAGENT HOST"

    def to_i13_host(self) -> dict:
        """Serialize the hosted subagent as an I-13 ATTRIBUTE data collapse."""
        return {
            "ATTRIBUTE": {
                "module": "subagent",
                "scope": "L2 SUBAGENT HOST",
                "name": self.name,
                "l2_address": self.l2_address,
                "host_symbol": self.host_symbol,
                "learned_i13": self.learned_i13,
                "proposes_operant": self.proposes_operant,
                "attestation_sha256": self.attestation_sha256,
            }
        }
