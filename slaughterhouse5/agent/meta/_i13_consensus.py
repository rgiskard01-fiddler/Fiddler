# -*- coding: utf-8 -*-
"""Universal consensus of all .agents who have LEARNED I-13 and EXTENDED the
language. Delegates to the agent.consensus library (single source of truth;
the README points here). Run by the daily cascade.

David 2026-08-01: "have daily cascade run a universal consensus of all .agents
who have learned i-13 and who have extended the language."
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)

from agent.consensus import FROZEN_SPEC_SHA, run_consensus  # noqa: E402

AGENTS = os.path.join(HERE, ".agents")
SPEC = os.path.join(HERE, "i-13", "i-13 v2", "i13-v2", "01-frozen-spec", "i13-stack-v2.json")


def _frozen_sha():
    # Prefer the declared identity read from the frozen spec when present;
    # otherwise fall back to the canonical constant (== the real I-13 v2 sha).
    if os.path.isfile(SPEC):
        try:
            import json
            return json.load(open(SPEC, encoding="utf-8")).get("sha256", FROZEN_SPEC_SHA)
        except Exception:
            pass
    return FROZEN_SPEC_SHA


def main():
    out = run_consensus(AGENTS, frozen=_frozen_sha())
    print("I-13 UNIVERSAL CONSENSUS:")
    print(f"  agents: {out['agents_count']} · all attest same frozen spec: {out['all_attest_same_spec']}")
    print(f"  consensus_root: {out['consensus_root'][:24]}…")
    print(f"  threshold: {out['supermajority_threshold']}/{out['agents_count']} · "
          f"adopted: {out['adopted_extensions'] or 'none (frozen 13 stand)'}")
    print(f"  tally: {out['proposal_tally']}")
    print("  wrote .agents/_i13_consensus.json + I13-CONSENSUS.md")


if __name__ == "__main__":
    main()
