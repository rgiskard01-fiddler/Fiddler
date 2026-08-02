# slaughterhouse5-agent

**`agent`** — the emitting agent that produces I-13 collapses, and the
**universal consensus** across every agent that has *learned* I-13 and
*extended* it.

Part of the learning scope `{i, c, sa, ssa}` of the I-13 program, inside
the Slaughterhouse5 OS:

```
-+[[-{ i^4 , c (cortex), agent , subagent }
     -{ f1 , f2 , f3 , f4 , constructor , jitonf } -]] +-
```

## What it does

An agent **learns** I-13 by **attesting** the same frozen spec sha (the
declared identity of I-13 v2 — the `i4` anchor), and **extends** the
language by **proposing** one candidate operant *beyond THE TWELVE*,
chosen **deterministically** from the agent's own content hash
(reproducible, never invented per run).

The **universal consensus** is two real, deterministic facts:
1. a Merkle **consensus root** over every agent's attestation-based
   attestation — it proves they all cite the identical frozen I-13 spec;
2. an **adoption tally** — a proposed operant enters the extended alphabet
   only on a **>= 2/3 supermajority**. The frozen thirteen stand otherwise.

This is conservative by design: a run with zero adoptions is an honest
outcome, not a failure. The root is deterministic — it changes only when
an agent is added or edited, never with the clock.

## Grounded constants (verbatim from the baseline)

* `FROZEN_SPEC_SHA = 64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8`
  — I-13 v2 FROZEN (== `i4`'s anchor).
* `THE_TWELVE` — NAME, CONSTANT, ATTRIBUTE, CALL, ASSIGN, ARG, EXPR, IF,
  COMPARE, FUNCTIONDEF, RETURN, BINOP.
* `OPERANT_POOL` — 12 candidate operants beyond THE TWELVE, each attributed
  to its historical originator (Lovelace, Church, Milner, Hoare, Liskov…).
  This records **lineage, not authorship**.

## Layout

* `agent/consensus.py` — the importable library (single source of truth):
  `Agent`, `propose_operant`, `merkle`, `consensus_from_agents`,
  `run_consensus`.
* `meta/_i13_consensus.py` — the daily-cascade entry point; **delegates** to
  `agent.consensus` (no duplicated logic).
* `tests/test_agent.py` — 10 tests.

## Usage

```bash
python -m agent.cli propose "agent payload"
python -m agent.cli attest "agent payload" --name a.agent
python -m agent.cli consensus path/to/.agents
pytest tests/
```

`run_consensus` scans every `.agent`/`.html`/`.md` in a directory, writes
`.agents/_i13_consensus.json` (machine registry) and `I13-CONSENSUS.md`
(human ledger). Idempotent and non-destructive.

## Relationship to the other modules

* `i4` supplies the frozen-spec identity every agent attests to.
* `subagent` is the **hosted** variant (L2 SUBAGENT HOST) — an agent plus a
  hosting layer.
* `constructor` folds collapses; an agent's attestation is itself a
  collapse that feeds the consensus root.

## Provenance

I-13 is human-directed and AI-co-authored (Hermes Agent, Nous Research).
The frozen-spec sha and operant attributions are drawn from the unified
baseline `I,Robot/hermes.i13`. AI co-creator credit is **provenance**, not
evidence of external derivation.
