#!/usr/bin/env python3
"""
i4 CLI - the I^4 identity root.

Subcommands
-----------
  identity <x>     apply the I operation (I(x) = the self)
  collapse [seed]  the I-collapse across all four planes
  attest <sha>     attest a claimed spec sha equals the frozen identity
  seed             print the frozen-spec identity anchors
  policy           emit the i4 identity as an I-13 data collapse
"""
from __future__ import annotations

import argparse
import json
import sys

from .i4 import (CONSENSUS_AGENTS, CONSENSUS_ROOT, FROZEN_SPEC_SHA, I4Collapse,
                 attest, i4_collapse, identity, to_i13_identity)


def _cmd_identity(args) -> int:
    print(f"I({args.x!r}) = {identity(args.x)!r}   (idempotent: I(I(x))==I(x))")
    return 0


def _cmd_collapse(args) -> int:
    seed = args.seed or FROZEN_SPEC_SHA
    c = i4_collapse(seed)
    print(f"seed : {seed}")
    for p in c.per_plane:
        print(f"  {p['plane']} {p['name']:14} {p['digest']}")
    print(f"I^4 root : {c.root}")
    return 0


def _cmd_attest(args) -> int:
    ok = attest(args.sha)
    print(f"claimed : {args.sha}")
    print(f"frozen  : {FROZEN_SPEC_SHA}")
    print(f"ATTEST  : {'OK' if ok else 'MISMATCH'}")
    return 0 if ok else 1


def _cmd_seed(args) -> int:
    print(f"frozen_spec_sha : {FROZEN_SPEC_SHA}")
    print(f"consensus_root  : {CONSENSUS_ROOT}")
    print(f"consensus_agents: {CONSENSUS_AGENTS}")
    return 0


def _cmd_policy(args) -> int:
    print(json.dumps(to_i13_identity(), indent=2))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="i4", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("identity"); p.add_argument("x"); p.set_defaults(func=_cmd_identity)
    p = sub.add_parser("collapse"); p.add_argument("seed", nargs="?"); p.set_defaults(func=_cmd_collapse)
    p = sub.add_parser("attest"); p.add_argument("sha"); p.set_defaults(func=_cmd_attest)
    p = sub.add_parser("seed"); p.set_defaults(func=_cmd_seed)
    p = sub.add_parser("policy"); p.set_defaults(func=_cmd_policy)
    ns = ap.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    raise SystemExit(main())
