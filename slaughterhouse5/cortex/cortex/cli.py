#!/usr/bin/env python3
"""
cortex CLI - inspect the L4 deep-operand plane and exercise its governance.

Subcommands
-----------
  planes            print the four-plane stack (nodes / address bits)
  resolve <addr>    resolve a deep operand by 13-bit L4 address
  veto --open FUNCTIONDEF --closer RETURN [--expect FUNCTIONDEF:RETURN]   apply the veto rule
  sense             show the cortex sensor feedback
  verify <trace.json>               verify a governance trace
  policy            emit the cortex governance as an I-13 data collapse
"""
from __future__ import annotations

import argparse
import json
import sys

from .cortex import (Cortex, L4_NODES, PLANES, PLANE_ORDER, RULE_REACH,
                     VETO_MSG)


def _cmd_planes(args) -> int:
    print(f"{'plane':5} {'name':16} {'nodes':>8} {'bits':>4}")
    for k in PLANE_ORDER:
        v = PLANES[k]
        print(f"{k:5} {v['name']:16} {v['nodes']:>8} {v['bits']:>4}")
    print(f"\nrule_reach (per 1000 nodes, L1..L4):")
    for r, vals in RULE_REACH.items():
        print(f"  {r:12}: {vals}")
    return 0


def _cmd_resolve(args) -> int:
    c = Cortex()
    try:
        op = c.resolve(int(args.addr))
    except Exception as e:
        print(f"VOID: {e}", file=sys.stderr)
        return 1
    print(f"addr    : {op.addr}  (13-bit L4)")
    print(f"tag     : {op.tag}")
    print(f"weight  : {op.weight:+.6f}  (deterministic stand-in for trained L4 weight)")
    return 0


def _cmd_veto(args) -> int:
    expect = {}
    for pair in args.expect or []:
        if ":" in pair:
            o, cl = pair.split(":", 1)
            expect[o] = cl
    allowed, why = Cortex.veto(args.open, args.closer, expect)
    print(f"open   : {args.open}")
    print(f"closer : {args.closer}")
    print(f"expect : {expect or '(match any)'}")
    print(f"{'ALLOWED' if allowed else 'VETOED'}: {why}")
    return 0 if allowed else 1


def _cmd_sense(args) -> int:
    print(json.dumps(Cortex().sense(), indent=2))
    return 0


def _cmd_verify(args) -> int:
    trace = json.load(open(args.trace, encoding="utf-8"))
    ok, report = Cortex().verify(trace)
    for line in report:
        print(line)
    print(f"\nVERIFY: {'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


def _cmd_policy(args) -> int:
    print(json.dumps(Cortex().to_i13_policy(), indent=2))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="cortex", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("planes"); p.set_defaults(func=_cmd_planes)
    p = sub.add_parser("resolve", help="resolve an L4 address")
    p.add_argument("addr"); p.set_defaults(func=_cmd_resolve)
    p = sub.add_parser("veto", help="apply the veto rule")
    p.add_argument("--open", nargs="+", required=True, help="open stack, most-recent last")
    p.add_argument("--closer", required=True, help="candidate closer")
    p.add_argument("--expect", nargs="*", default=[], help="opener:closer pairs")
    p.set_defaults(func=_cmd_veto)
    p = sub.add_parser("sense"); p.set_defaults(func=_cmd_sense)
    p = sub.add_parser("verify"); p.add_argument("trace"); p.set_defaults(func=_cmd_verify)
    p = sub.add_parser("policy"); p.set_defaults(func=_cmd_policy)

    ns = ap.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    raise SystemExit(main())
