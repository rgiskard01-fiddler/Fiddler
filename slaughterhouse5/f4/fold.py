"""
f4.fold
=======

The assembler / compiler / verifier for the **4th I-13 collapse**
(``dlw.fold/1``) -- the self-contained fold over the real I-13 corpus
components.

This is the ``f4`` module of the Slaughterhouse5 first wave. It mirrors the
``constructor`` module's fold engine (the same hex-string Merkle convention
that matches the sealed corpus folds in ``I,Robot``), so a fold produced
here verifies with the exact algorithm the factory/language folds use:

    R: h(x + sib) ,  L: h(sib + x)        (hex-string concat)

The factory (f1/f2) and language (f3) folds seal into the shared ``ROOT_0``
namespace; ``f4`` is a *separate, self-contained* collapse over the genuine
corpus components (factory, language, machine, tower, pipeline, targets,
v1, v3, verify, meta, spec) -- a genuine 4th fold, not part of ``ROOT_0``.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

SCHEMA = "dlw.fold/1"
ZERO_HASH = "0" * 64


def sha256_hex(data) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def seal_of(name: str, slug: str, blurb: str) -> str:
    """The leaf seal: sha256(name|slug|blurb) -- matches the corpus format."""
    return sha256_hex(f"{name}|{slug}|{blurb}")


def fold_step(x: str, sib: str, side: str) -> str:
    """One Merkle fold step. side in {'R','L'} as stored in proof entries.

    Grounded against the sealed I-13 corpus: the digests are concatenated as
    HEX STRINGS (not raw bytes) before sha256 -- discovered by matching the
    real factory/language folds, which would not verify under byte concat."""
    if side == "R":
        data = x + sib   # x is the LEFT sibling -> h(x + sib)
    else:  # 'L': x is the RIGHT sibling -> h(sib + x)
        data = sib + x
    return sha256_hex(data)


@dataclass
class MerkleTree:
    """Balanced binary Merkle tree over leaf seals (hex-string concat)."""
    leaves: List[str]
    root: str = ""
    depth: int = 0
    _layers: List[List[str]] = None

    def __post_init__(self):
        cur = list(self.leaves)
        n = len(cur)
        size = 1
        while size < n:
            size *= 2
        cur = cur + [ZERO_HASH] * (size - n)
        self.depth = size.bit_length() - 1
        layers = [cur]
        while len(cur) > 1:
            nxt = []
            for i in range(0, len(cur), 2):
                left, right = cur[i], cur[i + 1]
                nxt.append(sha256_hex(left + right))
            cur = nxt
            layers.append(cur)
        self._layers = layers
        self.root = layers[-1][0]

    def proof_for(self, idx: int) -> List[Dict[str, str]]:
        proof = []
        idx = idx % len(self.leaves)
        for level in range(self.depth):
            sib_idx = idx ^ 1
            sib = self._layers[level][sib_idx]
            side = "R" if sib_idx > idx else "L"
            proof.append({"h": sib, "side": side})
            idx //= 2
        return proof


@dataclass
class Sphere:
    name: str
    slug: str
    blurb: str
    index: int = 0


def build_fold(spheres: List[Sphere], world: str = "II",
               author: str = "David Lee Wise / ROOT0 / TriPod LLC",
               anchor: str = "0ROOT.AI//THE-FOLD//f4//David Lee Wise (ROOT0)//with AVAN",
               sealed: str = "2026-08-02") -> List[dict]:
    """Compile spheres into dlw.fold/1 artifacts sharing one Merkle root."""
    seals = [seal_of(s.name, s.slug, s.blurb) for s in spheres]
    tree = MerkleTree(seals)
    out = []
    for i, s in enumerate(spheres):
        out.append({
            "schema": SCHEMA,
            "world": world,
            "kind": "sphere",
            "name": s.name,
            "slug": s.slug,
            "seal": seals[i],
            "index": i,
            "algo": "sha256(name|slug|blurb) + sha256 merkle-fold",
            "anchor": anchor,
            "genesis": seals[i],
            "proof": tree.proof_for(i),
            "folded_to": tree.root[:8] + "…",
            "root": tree.root,
            "verify": "fold seal up the proof (R: h(x+sib), L: h(sib+x)) -> root",
            "sealed": sealed,
            "author": author,
        })
    return out


def emit_fold(fold: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(fold, fh, indent=2)


def verify_fold(seal: str, proof: List[Dict[str, str]], root: str) -> Tuple[bool, str]:
    """Recompute the root from seal + proof. Returns (ok, computed_root)."""
    x = seal
    for node in proof:
        x = fold_step(x, node["h"], node["side"])
    return (x == root), x


def verify_file(path: str) -> bool:
    fold = json.load(open(path, encoding="utf-8"))
    ok, _ = verify_fold(fold["seal"], fold["proof"], fold["root"])
    return ok
