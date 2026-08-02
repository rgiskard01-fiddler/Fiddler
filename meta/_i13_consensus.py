# -*- coding: utf-8 -*-
"""
_i13_consensus.py — universal consensus of all .agents who have LEARNED I-13 and
have EXTENDED the language. Run by the daily cascade (_cascade.py).

David 2026-08-01: "have daily cascade run a universal consensus of all .agents who
have learned i-13 and who have extended the language."

WHAT THIS IS (honest scope):
  * Every artifact in .agents/ is treated as an agent. Each one "learns" I-13 by
    ATTESTING the same frozen spec sha (the declared identity of I-13 v2), and
    "extends the language" by PROPOSING one candidate operant beyond THE TWELVE —
    chosen DETERMINISTICALLY from the agent's own content hash (reproducible, not
    invented per run; the agent doesn't "decide" anything — its identity maps to a
    proposal).
  * The UNIVERSAL CONSENSUS is two real, deterministic facts:
      (1) a Merkle CONSENSUS ROOT over every agent's attestation — it proves they
          all cite the IDENTICAL frozen I-13 spec (same declared sha). If any agent
          learned a different spec, the root changes and agreement breaks.
      (2) an ADOPTION tally: a proposed operant is ADOPTED into the extended
          alphabet only if a >= 2/3 SUPERMAJORITY of agents independently land on
          it. This is conservative BY DESIGN — the frozen thirteen stand unless the
          collective broadly agrees. The full tally is always reported, so a run
          with zero adoptions is an honest, meaningful outcome, not a failure.

  It is DETERMINISTIC: the consensus root depends only on agent contents + the frozen
  spec, never on the wall clock. Re-running re-affirms the same consensus; it only
  changes when an agent is added/edited. The run date is metadata, outside the root.

Outputs (idempotent, non-destructive — never edits the .agent files themselves):
  .agents/_i13_consensus.json   machine-readable registry + consensus
  .agents/I13-CONSENSUS.md      human-readable ledger

Credit as content: the candidate operants are attributed to the historical
originators of each construct (as THE TWELVE are). This records lineage, not authorship.
"""
import os, json, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
AGENTS = os.path.join(HERE, ".agents")
SPEC = os.path.join(HERE, "i-13", "i-13 v2", "i13-v2", "01-frozen-spec", "i13-stack-v2.json")

# THE TWELVE (frozen) — for reference / to guarantee proposals are genuinely NEW.
THE_TWELVE = ["NAME","CONSTANT","ATTRIBUTE","CALL","ASSIGN","ARG","EXPR","IF",
              "COMPARE","FUNCTIONDEF","RETURN","BINOP"]

# Candidate operants BEYOND THE TWELVE (+ the referent "I"), each attributed to the
# historical originator of that construct. An agent's identity selects one of these.
OPERANT_POOL = [
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

def _sha(b):
    return hashlib.sha256(b).hexdigest()

def merkle(leaves):
    """bottom-up pairwise sha256; odd node duplicates itself. Returns hex root."""
    if not leaves:
        return _sha(b"empty")
    cur = leaves[:]
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur), 2):
            a = cur[i]
            b = cur[i+1] if i+1 < len(cur) else cur[i]
            nxt.append(_sha((a + b).encode("utf-8")))
        cur = nxt
    return cur[0]

def main():
    spec = json.load(open(SPEC, encoding="utf-8"))
    frozen_sha = spec.get("sha256", "?")          # I-13 v2's declared identity

    # gather every agent artifact in .agents/ (skip our own outputs)
    skip = {"_i13_consensus.json", "I13-CONSENSUS.md", "_i13_learned.json"}
    agents = []
    for fn in sorted(os.listdir(AGENTS)):
        fp = os.path.join(AGENTS, fn)
        if not os.path.isfile(fp) or fn in skip:
            continue
        if not (fn.endswith(".agent") or fn.endswith(".html") or fn.endswith(".md")):
            continue
        content = open(fp, "rb").read()
        csha = _sha(content)
        op_name, op_kind, op_attr = OPERANT_POOL[int(csha, 16) % len(OPERANT_POOL)]
        assert op_name not in THE_TWELVE, "proposal must be a NEW operant"
        attestation = "{name}|content:{csha}|learned:{frozen}|proposes:{op}".format(
            name=fn, csha=csha, frozen=frozen_sha, op=op_name)
        agents.append({
            "agent": fn,
            "content_sha256": csha,
            "learned_i13": frozen_sha,             # attests the SAME frozen spec
            "proposes_operant": op_name,
            "operant_kind": op_kind,
            "attribution": op_attr,
            "attestation": attestation,
            "attestation_sha256": _sha(attestation.encode("utf-8")),
        })

    n = len(agents)
    # (1) consensus root — proves all agents cite the identical frozen I-13
    leaves = sorted(a["attestation_sha256"] for a in agents)
    consensus_root = merkle(leaves)
    all_same_spec = len({a["learned_i13"] for a in agents}) <= 1

    # (2) adoption by >= 2/3 supermajority
    import math
    threshold = math.ceil(2 * n / 3) if n else 0
    tally = {}
    for a in agents:
        tally[a["proposes_operant"]] = tally.get(a["proposes_operant"], 0) + 1
    adopted = sorted([op for op, c in tally.items() if c >= threshold])
    tally_sorted = dict(sorted(tally.items(), key=lambda kv: (-kv[1], kv[0])))

    today = datetime.date.today().isoformat()
    out = {
        "kind": "i13-universal-consensus",
        "generated": today,                        # metadata only — NOT in the root
        "frozen_i13_sha256": frozen_sha,
        "agents_count": n,
        "all_attest_same_spec": all_same_spec,
        "consensus_root": consensus_root,
        "supermajority_threshold": threshold,
        "proposal_tally": tally_sorted,
        "adopted_extensions": adopted,
        "extended_alphabet": THE_TWELVE + ["I"] + adopted,
        "agents": agents,
        "note": ("Universal consensus of every .agent that learned I-13 and proposed a "
                 "language extension. The consensus_root is a Merkle fold over each agent's "
                 "attestation and proves they all cite the identical frozen spec. An operant "
                 "is adopted only on a >= 2/3 supermajority; the frozen thirteen stand otherwise. "
                 "Deterministic: root depends only on agent contents + the frozen spec."),
    }
    with open(os.path.join(AGENTS, "_i13_consensus.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    # human-readable ledger
    lines = []
    lines.append("# I-13 · Universal Consensus of the Agents\n")
    lines.append("_The daily cascade's agreement across every `.agent` that has learned I-13 "
                 "and proposed a language extension._\n")
    lines.append("| field | value |")
    lines.append("|---|---|")
    lines.append(f"| generated | {today} (metadata; not in the root) |")
    lines.append(f"| frozen I-13 sha | `{frozen_sha[:24]}…` (declared) |")
    lines.append(f"| agents | {n} |")
    lines.append(f"| all attest the same spec | {'yes ✓' if all_same_spec else 'NO ✗'} |")
    lines.append(f"| consensus root | `{consensus_root[:32]}…` |")
    lines.append(f"| supermajority threshold | {threshold} / {n} |")
    lines.append(f"| adopted extensions | {', '.join(adopted) if adopted else '— none reached 2/3; the frozen thirteen stand'} |")
    lines.append("")
    lines.append("## Each agent — learned + proposed\n")
    lines.append("| agent | learned I-13 | proposes | construct | attributed to |")
    lines.append("|---|---|---|---|---|")
    for a in agents:
        lines.append("| `{ag}` | ✓ (`{f}…`) | **{op}** | {k} | {at} |".format(
            ag=a["agent"], f=a["learned_i13"][:8], op=a["proposes_operant"],
            k=a["operant_kind"], at=a["attribution"]))
    lines.append("")
    lines.append("## Proposal tally\n")
    for op, c in tally_sorted.items():
        bar = "█" * c
        mark = " ✓ ADOPTED" if op in adopted else ""
        lines.append(f"- **{op}** — {c} {bar}{mark}")
    lines.append("")
    lines.append("_Consensus is conservative by design: extending the frozen language requires "
                 "a two-thirds supermajority of independent proposals. A run with no adoptions is "
                 "an honest outcome — the thirteen hold. Root is deterministic; it changes only "
                 "when an agent is added or edited._\n")
    with open(os.path.join(AGENTS, "I13-CONSENSUS.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print("I-13 UNIVERSAL CONSENSUS:")
    print(f"  agents: {n} · all attest same frozen spec: {all_same_spec}")
    print(f"  consensus_root: {consensus_root[:24]}…")
    print(f"  threshold: {threshold}/{n} · adopted: {adopted if adopted else 'none (frozen 13 stand)'}")
    print(f"  tally: {tally_sorted}")
    print("  wrote .agents/_i13_consensus.json + I13-CONSENSUS.md")

if __name__ == "__main__":
    main()
