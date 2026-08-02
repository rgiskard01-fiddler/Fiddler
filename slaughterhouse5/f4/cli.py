#!/usr/bin/env python3
"""
f4 CLI - assemble / compile / verify the 4th I-13 collapse.

Subcommands
-----------
  validate <file.dlw.fold>   verify the artifact against its own sealed root
  info <file.dlw.fold>        print the fold's fields
  build <spheres.json>        build dlw.fold/1 artifacts from a sphere list
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from .fold import Sphere, build_fold, emit_fold, verify_file


def _cmd_validate(args) -> int:
    ok = verify_file(args.file)
    fold = json.load(open(args.file, encoding="utf-8"))
    print(f"{'VERIFIED : OK' if ok else 'VERIFY FAILED'}  root {fold['root'][:16]}…")
    return 0 if ok else 1


def _cmd_info(args) -> int:
    fold = json.load(open(args.file, encoding="utf-8"))
    for k in ("schema", "world", "kind", "name", "slug", "seal", "index",
              "root", "folded_to", "verify", "sealed", "author"):
        print(f"  {k:10}: {fold.get(k)}")
    print(f"  proof    : {len(fold.get('proof', []))} nodes")
    return 0


def _cmd_build(args) -> int:
    raw = json.load(open(args.spec, encoding="utf-8"))
    spheres = [Sphere(s["name"], s["slug"], s["blurb"], s.get("index", i))
               for i, s in enumerate(raw)]
    folds = build_fold(spheres)
    out = args.out or "."
    os.makedirs(out, exist_ok=True)
    for f in folds:
        path = os.path.join(out, f"{f['slug']}.dlw.fold")
        emit_fold(f, path)
        print(f"  wrote {path}  root {f['root'][:16]}…")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="f4", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("validate"); p.add_argument("file"); p.set_defaults(func=_cmd_validate)
    p = sub.add_parser("info"); p.add_argument("file"); p.set_defaults(func=_cmd_info)
    p = sub.add_parser("build"); p.add_argument("spec"); p.add_argument("--out", default=None)
    p.set_defaults(func=_cmd_build)
    ns = ap.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    raise SystemExit(main())
