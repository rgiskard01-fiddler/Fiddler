#!/usr/bin/env python3
"""
agent CLI - emit I-13 collapses and compute universal consensus.

Subcommands
-----------
  propose <content>          deterministic operant beyond THE TWELVE
  attest <content>           attestation string citing the frozen spec
  propose-file <path>        propose from a file's content
  consensus <agents_dir>     scan .agents/, write consensus ledgers
"""
from __future__ import annotations

import argparse
import json
import sys

from .consensus import (FROZEN_SPEC_SHA, Agent, consensus_from_agents,
                        run_consensus)


def _cmd_propose(args) -> int:
    from .consensus import propose_operant, sha256_hex
    csha = sha256_hex(args.content)
    name, kind, attr = propose_operant(csha)
    print(f"content_sha : {csha}")
    print(f"proposes    : {name} ({kind})")
    print(f"attributed  : {attr}")
    return 0


def _cmd_attest(args) -> int:
    a = Agent.from_content(args.name or "stdin", args.content.encode("utf-8"))
    print(a.attestation)
    print(f"sha256: {a.attestation_sha256}")
    return 0


def _cmd_propose_file(args) -> int:
    from .consensus import propose_operant, sha256_hex
    csha = sha256_hex(open(args.path, "rb").read())
    name, kind, attr = propose_operant(csha)
    print(f"file       : {args.path}")
    print(f"content_sha : {csha}")
    print(f"proposes    : {name} ({kind}) -> {attr}")
    return 0


def _cmd_consensus(args) -> int:
    out = run_consensus(args.dir)
    print("I-13 UNIVERSAL CONSENSUS:")
    print(f"  agents: {out['agents_count']} · all attest same frozen spec: {out['all_attest_same_spec']}")
    print(f"  consensus_root: {out['consensus_root'][:24]}…")
    print(f"  threshold: {out['supermajority_threshold']}/{out['agents_count']} · adopted: {out['adopted_extensions'] or 'none (frozen 13 stand)'}")
    print(f"  tally: {out['proposal_tally']}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="agent", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("propose"); p.add_argument("content"); p.set_defaults(func=_cmd_propose)
    p = sub.add_parser("attest"); p.add_argument("content"); p.add_argument("--name", default="stdin"); p.set_defaults(func=_cmd_attest)
    p = sub.add_parser("propose-file"); p.add_argument("path"); p.set_defaults(func=_cmd_propose_file)
    p = sub.add_parser("consensus"); p.add_argument("dir"); p.set_defaults(func=_cmd_consensus)
    ns = ap.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    raise SystemExit(main())
