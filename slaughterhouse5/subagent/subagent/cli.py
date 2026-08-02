#!/usr/bin/env python3
"""
subagent CLI - the L2 SUBAGENT HOST: a hosted I-13 learner.

Subcommands
-----------
  host <content> [--addr N]   host a subagent on an 18-bit L2 address
  propose <content>           deterministic operant beyond THE TWELVE
  verify <content>            run the cortex-style hosting boundary check
  planes                      print the L2 SUBAGENT HOST plane
  policy                      emit the hosted subagent as an I-13 data collapse
"""
from __future__ import annotations

import argparse
import json
import sys

from .subagent import (HOST_ALPHABET_SIZE, L2_ADDR_MAX, L2_BITS, L2_NODES,
                       SubAgent)


def _cmd_host(args) -> int:
    addr = int(args.addr) if args.addr is not None else None
    sa = SubAgent.from_content(args.name or "subagent", args.content.encode("utf-8"), l2_address=addr)
    print(f"name        : {sa.name}")
    print(f"content_sha : {sa.content_sha256}")
    print(f"learned     : {sa.learned_i13[:24]}…")
    print(f"proposes    : {sa.proposes_operant} ({sa.operant_kind})")
    print(f"L2 address  : {sa.l2_address}  (18-bit, 0..{L2_ADDR_MAX})")
    print(f"host symbol : {sa.host_symbol}")
    ok, why = sa.verify_host()
    print(f"hosting     : {'OK' if ok else 'FAIL'} — {why}")
    return 0 if ok else 1


def _cmd_propose(args) -> int:
    from .subagent import propose_operant, sha256_hex
    csha = sha256_hex(args.content)
    name, kind, attr = propose_operant(csha)
    print(f"proposes: {name} ({kind}) -> {attr}")
    return 0


def _cmd_verify(args) -> int:
    sa = SubAgent.from_content(args.name or "subagent", args.content.encode("utf-8"))
    ok, why = sa.verify_host()
    print(f"{'OK' if ok else 'FAIL'}: {why}")
    return 0 if ok else 1


def _cmd_planes(args) -> int:
    print(f"L2 SUBAGENT HOST: {L2_NODES} nodes / {L2_BITS} bits")
    print(f"18-bit address space: 0..{L2_ADDR_MAX}")
    print(f"host alphabet size : {HOST_ALPHABET_SIZE}")
    return 0


def _cmd_policy(args) -> int:
    sa = SubAgent.from_content(args.name or "subagent", args.content.encode("utf-8"))
    print(json.dumps(sa.to_i13_host(), indent=2))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="subagent", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("host"); p.add_argument("content"); p.add_argument("--name", default="subagent")
    p.add_argument("--addr", default=None); p.set_defaults(func=_cmd_host)
    p = sub.add_parser("propose"); p.add_argument("content"); p.set_defaults(func=_cmd_propose)
    p = sub.add_parser("verify"); p.add_argument("content"); p.add_argument("--name", default="subagent")
    p.set_defaults(func=_cmd_verify)
    p = sub.add_parser("planes"); p.set_defaults(func=_cmd_planes)
    p = sub.add_parser("policy"); p.add_argument("content"); p.add_argument("--name", default="subagent")
    p.set_defaults(func=_cmd_policy)
    ns = ap.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    raise SystemExit(main())
