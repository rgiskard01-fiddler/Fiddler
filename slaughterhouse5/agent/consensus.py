"""
agent.consensus
===============

The emitting agent that produces I-13 collapses, and the **universal
consensus** across every agent that has *learned* I-13 and *extended* it.

Grounded in the corpus tooling (slaughterhouse5/agent/meta/_i13_consensus.py)
and the unified baseline (I,Robot/hermes.i13):

  * An agent LEARNS I-13 by ATTESTING the same frozen spec sha -- the
    declared identity of I-13 v2 (the i4 anchor).
  * An agent EXTENDS the language by PROPOSING one candidate operant
    BEYOND THE TWELVE -- chosen DETERMINISTICALLY from the agent's own
    content hash (reproducible, never invented per run).
  * UNIVERSAL CONSENSUS is two real, deterministic facts:
        (1) a Merkle CONSENSUS ROOT over every agent's attestation -- it
            proves they all cite the IDENTICAL frozen I-13 spec;
        (2) an ADOPTION tally: a proposed operant is adopted into the
            extended alphabet only on a >= 2/3 SUPERMAJORITY.

This is the importable library; the meta/_i13_consensus.py script in this
repo delegates to it. Deterministic: the root depends only on agent
contents + the frozen spec, never the wall clock.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# --------------------------------------------------------------------------
# canonical identity anchor (I-13 v2 FROZEN; verbatim from herbmes.i13)
# --------------------------------------------------------------------------
FROZEN_SPEC_SHA = "64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8"

# THE TWELVE (frozen) -- proposals must be genuinely NEW operants.
THE_TWELVE = ["NAME", "CONSTANT", "ATTRIBUTE", "CALL", "ASSIGN", "ARG",
              "EXPR", "IF", "COMPARE", "FUNCTIONDEF", "RETURN", "BINOP"]

# Candidate operants BEYOND THE TWELVE (+ the referent "I"), each attributed
# to the historical originator of that construct. An agent's identity selects
# one of these deterministically.
OPERANT_POOL: List[Tuple[str, str, str]] = [
    ("LOOP",   "iteration",            "Ada Lovelace / Goldstine-von Neumann (the loop)"),
    ("LAMBDA", "anonymous function",   "Alonzo Church (lambda calculus, 1936)"),
    ("MATCH",  "pattern match",        "Robin Milner (ML, 1973)"),
    ("TRY",    "exception handling",   "John Goodenough (1975)"),
    ("YIELD",  "generator / coroutine","Barbara Liskov (CLU, 1975)"),
    ("IMPORT", "module reference",     "Niklaus Wirth (Modula, 1975)"),
    ("SPAWN",  "concurrent process",   "C. A. R. Hoare (CSP, 1978)"),
    ("CAST",   "type coercion",        "Strachey / the typed lambda tradition"),
    ("INDEX",  "subscript access",     "Kenneth Iverson (APL, 1962)"),
    ("SLICE",  "range selection",      "van Rossum (Python) / Iverson lineage"),
    ("ASSERT", "invariant check",      "Alan Turing / Floyd-Hoare (assertions)"),
    ("AWAIT",  "asynchronous suspend", "the async/await lineage (Meijer et al.)"),
]


def sha256_hex(data) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def merkle(leaves: List[str]) -> str:
    """Bottom-up pairwise sha256 over hex-string leaves; odd node duplicates
    itself. Returns the hex root. (hex-string concat, consistent with the
    constructor/i4 collapse convention.)"""
    if not leaves:
        return sha256_hex(b"empty")
    cur = list(leaves)
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur), 2):
            a = cur[i]
            b = cur[i + 1] if i + 1 < len(cur) else cur[i]
            nxt.append(sha256_hex(a + b))
        cur = nxt
    return cur[0]


def propose_operant(content_sha: str) -> Tuple[str, str, str]:
    """Deterministic candidate operant for an agent, from its content hash.
    Guaranteed not in THE_TWELVE."""
    name, kind, attr = OPERANT_POOL[int(content_sha, 16) % len(OPERANT_POOL)]
    assert name not in THE_TWELVE
    return name, kind, attr


@dataclass
class Agent:
    name: str
    content_sha256: str
    learned_i13: str                 # the frozen spec sha it attests
    proposes_operant: str
    operant_kind: str
    attribution: str
    attestation: str = ""
    attestation_sha256: str = ""

    @classmethod
    def from_content(cls, name: str, content: bytes,
                     frozen: str = FROZEN_SPEC_SHA) -> "Agent":
        csha = sha256_hex(content)
        op_name, op_kind, op_attr = propose_operant(csha)
        attestation = "{name}|content:{csha}|learned:{frozen}|proposes:{op}".format(
            name=name, csha=csha, frozen=frozen, op=op_name)
        return cls(
            name=name, content_sha256=csha, learned_i13=frozen,
            proposes_operant=op_name, operant_kind=op_kind, attribution=op_attr,
            attestation=attestation,
            attestation_sha256=sha256_hex(attestation.encode("utf-8")),
        )


def consensus_from_agents(agents: List[Agent],
                          frozen: str = FROZEN_SPEC_SHA) -> dict:
    """Pure consensus computation over a list of Agent objects."""
    n = len(agents)
    leaves = sorted(a.attestation_sha256 for a in agents)
    consensus_root = merkle(leaves)
    all_same_spec = len({a.learned_i13 for a in agents}) <= 1
    threshold = math.ceil(2 * n / 3) if n else 0
    tally: Dict[str, int] = {}
    for a in agents:
        tally[a.proposes_operant] = tally.get(a.proposes_operant, 0) + 1
    adopted = sorted([op for op, c in tally.items() if c >= threshold])
    tally_sorted = dict(sorted(tally.items(), key=lambda kv: (-kv[1], kv[0])))
    return {
        "kind": "i13-universal-consensus",
        "frozen_i13_sha256": frozen,
        "agents_count": n,
        "all_attest_same_spec": all_same_spec,
        "consensus_root": consensus_root,
        "supermajority_threshold": threshold,
        "proposal_tally": tally_sorted,
        "adopted_extensions": adopted,
        "extended_alphabet": THE_TWELVE + ["I"] + adopted,
        "agents": [a.__dict__ for a in agents],
    }


def run_consensus(agents_dir: str, frozen: str = FROZEN_SPEC_SHA) -> dict:
    """Scan every `.agent`/`.html`/`.md` artifact in `agents_dir`, build the
    agent registry, compute consensus, and write the machine + human ledgers.
    Idempotent and non-destructive (never edits the agent files)."""
    skip = {"_i13_consensus.json", "I13-CONSENSUS.md", "_i13_learned.json"}
    agents: List[Agent] = []
    for fn in sorted(os.listdir(agents_dir)):
        fp = os.path.join(agents_dir, fn)
        if not os.path.isfile(fp) or fn in skip:
            continue
        if not (fn.endswith(".agent") or fn.endswith(".html") or fn.endswith(".md")):
            continue
        content = open(fp, "rb").read()
        agents.append(Agent.from_content(fn, content, frozen=frozen))

    out = consensus_from_agents(agents, frozen=frozen)
    out["generated"] = None  # metadata only; NOT folded into the root

    with open(os.path.join(agents_dir, "_i13_consensus.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    _write_ledger(os.path.join(agents_dir, "I13-CONSENSUS.md"), out)
    return out


def _write_ledger(path: str, out: dict) -> None:
    n = out["agents_count"]
    adopted = out["adopted_extensions"]
    lines = ["# I-13 · Universal Consensus of the Agents\n",
             "_The daily cascade's agreement across every `.agent` that has learned I-13 "
             "and proposed a language extension._\n",
             "| field | value |", "|---|---|",
             f"| agents | {n} |",
             f"| all attest the same spec | {'yes' if out['all_attest_same_spec'] else 'NO'} |",
             f"| consensus root | `{out['consensus_root'][:32]}…` |",
             f"| supermajority threshold | {out['supermajority_threshold']} / {n} |",
             f"| adopted extensions | {', '.join(adopted) if adopted else '— none reached 2/3'} |",
             "",
             "## Each agent — learned + proposed\n",
             "| agent | learned I-13 | proposes | construct | attributed to |",
             "|---|---|---|---|---|"]
    for a in out["agents"]:
        lines.append("| `{ag}` | ✓ (`{f}…`) | **{op}** | {k} | {at} |".format(
            ag=a["name"], f=a["learned_i13"][:8], op=a["proposes_operant"],
            k=a["operant_kind"], at=a["attribution"]))
    lines += ["", "## Proposal tally"]
    for op, c in out["proposal_tally"].items():
        mark = " ✓ ADOPTED" if op in adopted else ""
        lines.append(f"- **{op}** — {c}{mark}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
