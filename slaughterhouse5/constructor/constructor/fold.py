"""
constructor.fold
================

The assembler / compiler / verifier for the I-13 *collapse* format
(``dlw.fold/1``), the sealed Merkle structure produced by THE FACTORY
and THE LANGUAGE spheres.

A fold is a binary Merkle tree built over the ``seal`` of one or more
spheres.  Each sphere carries its own inclusion proof:

    proof : [ {h, side}, ... ]      # siblings from leaf -> root
    root  : <hex>                   # the folded-up tree root

The fold step is exact (see any .dlw.fold ``verify`` field):

    R : node = sha256(x  + sib)     # sibling on the right  -> x is left
    L : node = sha256(sib + x)      # sibling on the left   -> x is right

This module implements three roles:

  * COMPILER  - ``build_fold`` / ``emit_fold`` : from a list of spheres
                (name, slug, blurb) compute seals, assemble the Merkle
                tree, and write one ``dlw.fold/1`` artifact per sphere.
  * ASSEMBLER - ``merkle_tree`` / ``proof_for`` : the low level tree
                assembly and per-leaf proof extraction.
  * INTERPRETER / VERIFIER - ``verify_fold`` / ``verify_file`` : recompute
                root from a seal + proof and compare to the sealed root.

No cryptography is invented: only sha256 over concatenated 32-byte
digests, exactly as the corpus ``verify`` string prescribes.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

SCHEMA = "dlw.fold/1"
ZERO_HASH = hashlib.sha256(b"\x00" * 32).hexdigest()  # sparse-tree padding leaf


# --------------------------------------------------------------------------
# low level hashing
# --------------------------------------------------------------------------
def sha256_hex(data) -> str:
    """sha256 of `data` (bytes or str) -> hex digest."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def seal_of(name: str, slug: str, blurb: str = "") -> str:
    """Leaf digest: sha256(name|slug|blurb) -- the 'seal' of a sphere."""
    return sha256_hex(f"{name}|{slug}|{blurb}".encode("utf-8"))


def fold_step(x: str, sib: str, side: str) -> str:
    """
    One Merkle fold step. side in {'R','L'} as stored in proof entries.

    Grounded against the sealed I-13 corpus: the digests are concatenated
    as HEX STRINGS (not raw bytes) before hashing, exactly reproducing
    THE FACTORY / THE LANGUAGE folds to their shared ROOT_0.

        R : node = sha256(x  + sib)   # sibling on the right -> x is left
        L : node = sha256(sib + x)    # sibling on the left  -> x is right
    """
    if side == "R":            # sibling on the right -> x is left
        return sha256_hex(x + sib)
    elif side == "L":          # sibling on the left  -> x is right
        return sha256_hex(sib + x)
    raise ValueError(f"bad side {side!r} (expected 'R' or 'L')")


# --------------------------------------------------------------------------
# assembler: Merkle tree over a list of leaf digests
# --------------------------------------------------------------------------
@dataclass
class MerkleTree:
    """Balanced binary Merkle tree padded to a power of two with ZERO_HASH."""
    leaves: List[str]
    layers: List[List[str]] = field(default_factory=list)
    root: str = ""

    def __post_init__(self):
        if not self.leaves:
            raise ValueError("MerkleTree needs at least one leaf")
        n = len(self.leaves)
        size = 1
        while size < n:
            size *= 2
        base = list(self.leaves) + [ZERO_HASH] * (size - n)
        layers = [base]
        cur = base
        while len(cur) > 1:
            nxt = []
            for i in range(0, len(cur), 2):
                left, right = cur[i], cur[i + 1]
                # hex-string concat (matches folded corpus convention)
                nxt.append(sha256_hex(left + right))
            layers.append(nxt)
            cur = nxt
        self.layers = layers
        self.root = layers[-1][0]
        self._depth = len(layers) - 1

    @property
    def depth(self) -> int:
        return self._depth

    def proof_for(self, index: int) -> List[Tuple[str, str]]:
        """Return [(sibling_hex, side), ...] from leaf up to (but not incl.) root."""
        if not (0 <= index < len(self.leaves)):
            raise IndexError(f"leaf index {index} out of range")
        proof = []
        idx = index
        for level in range(self._depth):
            sib_idx = idx ^ 1
            sib = self.layers[level][sib_idx]
            side = "R" if sib_idx > idx else "L"   # sibling on right -> we are left
            proof.append((sib, side))
            idx //= 2
        return proof


# --------------------------------------------------------------------------
# verifier: recompute root from a single seal + its proof
# --------------------------------------------------------------------------
def verify_fold(seal: str, proof: List[dict], root: str) -> Tuple[bool, str]:
    """
    Recompute the root by folding ``seal`` through ``proof``.

    Returns (matched, computed_root).  ``proof`` entries are dicts
    ``{"h": <hex>, "side": "R"|"L"}`` ordered leaf -> root.
    """
    x = seal
    for entry in proof:
        sib = entry["h"]
        side = entry["side"]
        x = fold_step(x, sib, side)
    return (x == root), x


def verify_file(path: str) -> Tuple[bool, str]:
    """Load a ``.dlw.fold`` artifact and verify its own seal -> root."""
    with open(path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    ok, computed = verify_fold(doc["seal"], doc["proof"], doc["root"])
    return ok, computed


# --------------------------------------------------------------------------
# compiler: build a full dlw.fold artifact from a sphere spec
# --------------------------------------------------------------------------
@dataclass
class Sphere:
    name: str
    slug: str
    blurb: str = ""
    index: int = 0
    author: str = "David Lee Wise / ROOT0 / TriPod LLC"


def build_fold(spheres: List[Sphere], *, world: str = "II",
               anchor: str = "0ROOT.AI//THE-FOLD//4096->0//David Lee Wise (ROOT0)//with AVAN",
               genesis: str = "") -> List[dict]:
    """
    Compile a list of spheres into ``dlw.fold/1`` artifacts (one per sphere),
    all sharing the same Merkle ``root``.

    Each artifact is the canonical collapse record:
        { schema, world, kind, name, slug, seal, index, algo, anchor,
          genesis, proof, folded_to, root, verify, sealed, author }
    """
    seals = [seal_of(s.name, s.slug, s.blurb) for s in spheres]
    tree = MerkleTree(seals)
    if not genesis:
        # deterministic genesis marker = root of an empty companion namespace
        genesis = sha256_hex(tree.root.encode("utf-8"))
    out = []
    for i, s in enumerate(spheres):
        proof = [{"h": h, "side": side} for (h, side) in tree.proof_for(i)]
        doc = {
            "schema": SCHEMA,
            "world": world,
            "kind": "sphere",
            "name": s.name,
            "slug": s.slug,
            "seal": seals[i],
            "index": s.index,
            "algo": "sha256(name|slug|blurb) + sha256 merkle-fold",
            "anchor": anchor,
            "genesis": genesis,
            "proof": proof,
            "folded_to": "ROOT_0",
            "root": tree.root,
            "verify": "fold seal up the proof (R: h(x+sib), L: h(sib+x)) -> root",
            "sealed": _today(),
            "author": s.author,
        }
        out.append(doc)
    return out


def emit_fold(spheres: List[Sphere], out_dir: str) -> List[str]:
    """Write one ``<slug>.dlw.fold`` per sphere; return written paths."""
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for doc in build_fold(spheres):
        path = os.path.join(out_dir, f"{doc['slug']}.dlw.fold")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2)
            fh.write("\n")
        written.append(path)
    return written


def _today() -> str:
    import datetime
    return datetime.date.today().isoformat()


# --------------------------------------------------------------------------
# bridge: represent a fold as an I-13 *data collapse* (ATTRIBUTE tree).
# This is the serialization handed to jitonf as structured data; it is
# NOT an executable I-13 program (sha256 is not an IVM-13-S opcode). The
# constructor performs the crypto; jitonf executes I-13 programs.
# --------------------------------------------------------------------------
def to_i13_collapse(doc: dict) -> dict:
    """Serialize a dlw.fold artifact as an I-13 ATTRIBUTE data collapse."""
    return {
        "ATTRIBUTE": {
            "schema": doc.get("schema"),
            "name": doc.get("name"),
            "slug": doc.get("slug"),
            "seal": doc.get("seal"),
            "root": doc.get("root"),
            "index": doc.get("index"),
            "proof": [{"h": p["h"], "side": p["side"]} for p in doc.get("proof", [])],
        }
    }
