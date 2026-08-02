"""
scripts/gen_fold.py - build the genuine f4 collapse from the real I-13 corpus.

It hashes every real I-13 component in I,Robot (factory, language, machine,
tower, pipeline, targets, v1, v3, verify, meta, spec), assembles them into a
single Merkle tree (hex-string concat), and emits f4's fold for the MACHINE
sphere -- f4 seals the machine that `jitonf` runs. The root depends on every
real component, so the collapse is genuinely grounded in the corpus.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)

from f4.fold import Sphere, build_fold, emit_fold  # noqa: E402

CORPUS = r"C:\Davids files\hermes agent\I,Robot"
OUT = os.path.join(REPO, "f4-machine.dlw.fold")

COMPONENTS = ["factory", "language", "machine", "tower", "pipeline",
              "targets", "v1", "v3", "verify", "meta", "spec"]


def component_digest(name: str) -> str:
    d = hashlib.sha256()
    base = os.path.join(CORPUS, name)
    if not os.path.isdir(base):
        return "0" * 64
    rows = []
    for root, _, files in os.walk(base):
        if ".git" in root.split(os.sep):
            continue
        for f in files:
            p = os.path.join(root, f)
            rows.append((os.path.relpath(p, base), hashlib.sha256(open(p, "rb").read()).hexdigest()))
    rows.sort()
    d.update(json.dumps(rows).encode("utf-8"))
    return d.hexdigest()


def main():
    spheres: list[Sphere] = []
    digests = {}
    for c in COMPONENTS:
        dg = component_digest(c)
        digests[c] = dg
        spheres.append(Sphere(f"I-13 · {c.upper()}", f"i13-{c}", dg, len(spheres)))
    # aggregate "THE BUILD" sphere over all digests
    agg = "".join(digests[c] for c in COMPONENTS)
    spheres.append(Sphere("I-13 · THE BUILD", "i13-build", agg, len(spheres)))

    folds = build_fold(spheres)
    # emit the MACHINE sphere's fold (f4 seals the machine jitonf runs)
    machine = next(f for f in folds if f["slug"] == "i13-machine")
    emit_fold(machine, OUT)

    # also write every component fold for reference
    ref = os.path.join(REPO, "f4-components.json")
    json.dump(folds, open(ref, "w", encoding="utf-8"), indent=2)

    print(f"components hashed : {len(COMPONENTS)}")
    print(f"tree root         : {machine['root']}")
    print(f"machine seal      : {machine['seal']}")
    print(f"machine proof len : {len(machine['proof'])}")
    print(f"wrote {OUT}")
    print(f"wrote {ref}")


if __name__ == "__main__":
    main()
