#!/usr/bin/env python3
"""
constructor CLI - assemble / compile / verify I-13 collapses.

Subcommands
-----------
  validate <file.dlw.fold>      verify the artifact against its own sealed root
  info     <file.dlw.fold>      print the fold's metadata + root
  build    <spheres.json>       compile spheres -> .dlw.fold artifacts
  tree     <file.dlw.fold>      show the leaf -> root fold path

spheres.json shape:
  [ {"name": "...", "slug": "...", "blurb": "...", "index": 0}, ... ]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from .fold import (
    MerkleTree,
    Sphere,
    build_fold,
    emit_fold,
    seal_of,
    verify_file,
    verify_fold,
)


def _cmd_validate(args) -> int:
    ok, computed = verify_file(args.file)
    doc = json.load(open(args.file, encoding="utf-8"))
    print(f"file     : {args.file}")
    print(f"seal     : {doc['seal']}")
    print(f"root     : {doc['root']}")
    print(f"computed : {computed}")
    print(f"VERIFIED : {'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


def _cmd_info(args) -> int:
    doc = json.load(open(args.file, encoding="utf-8"))
    for k in ("schema", "world", "kind", "name", "slug", "seal", "index",
              "algo", "anchor", "genesis", "folded_to", "root", "verify",
              "sealed", "author"):
        if k in doc:
            print(f"{k:9}: {doc[k]}")
    print(f"proof   : {len(doc.get('proof', []))} sibling hashes")
    return 0


def _cmd_build(args) -> int:
    raw = json.load(open(args.spheres, encoding="utf-8"))
    spheres = [
        Sphere(
            name=s["name"], slug=s["slug"],
            blurb=s.get("blurb", ""), index=s.get("index", 0),
            author=s.get("author", Sphere.author),
        )
        for s in raw
    ]
    out = args.out or os.path.dirname(os.path.abspath(args.spheres)) or "."
    written = emit_fold(spheres, out)
    # verify every emitted artifact round-trips
    for w in written:
        ok, _ = verify_file(w)
        if not ok:
            print(f"FAIL self-verify: {w}", file=sys.stderr)
            return 1
    print(f"built {len(written)} collapse(s) into {out}:")
    for w in written:
        print("  -", os.path.basename(w))
    return 0


def _cmd_tree(args) -> int:
    doc = json.load(open(args.file, encoding="utf-8"))
    ok, computed = verify_fold(doc["seal"], doc["proof"], doc["root"])
    print(f"leaf (seal): {doc['seal']}")
    for i, p in enumerate(doc["proof"]):
        print(f"  L{i:02d} {p['side']} sib={p['h']}")
    print(f"root       : {doc['root']}")
    print(f"VERIFIED   : {'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="constructor", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("validate", help="verify a .dlw.fold against its root")
    p.add_argument("file"); p.set_defaults(func=_cmd_validate)

    p = sub.add_parser("info", help="print fold metadata")
    p.add_argument("file"); p.set_defaults(func=_cmd_info)

    p = sub.add_parser("build", help="compile spheres -> folds")
    p.add_argument("spheres"); p.add_argument("--out", default=None)
    p.set_defaults(func=_cmd_build)

    p = sub.add_parser("tree", help="show the fold path")
    p.add_argument("file"); p.set_defaults(func=_cmd_tree)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
