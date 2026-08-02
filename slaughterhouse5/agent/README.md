========================================================================
| agent — emitting learner + universal consensus                       |
========================================================================


**agent** is the emitting agent that produces I-13 collapses, and the
**universal consensus** across every agent that has *learned* I-13 and
*extended* it.

## What it does
- **Attest** — each agent learns I-13 by attesting the frozen spec sha (the
  `i4` anchor) and **proposes** a deterministic operant beyond THE TWELVE,
  chosen by content hash (reproducible, never invented per run).
- **Universal consensus** — two real, deterministic facts:
  1. a Merkle **consensus root** over every agent's attestation (proves they
     cite the identical frozen spec);
  2. an **adoption tally** — a proposed operant enters the extended alphabet
     only on a ≥ 2/3 supermajority. The frozen thirteen stand otherwise.

A run with zero adoptions is an honest outcome, not a failure — the root is
deterministic and changes only when an agent is added or edited.

## Grounded constants
`FROZEN_SPEC_SHA`, `THE_TWELVE`, and `OPERANT_POOL` (12 candidate operants
beyond THE TWELVE, each attributed to its historical originator — lineage,
not authorship) are drawn from `hermes.i13`.

## Usage
```bash
python -m agent.cli propose "agent payload"
python -m agent.cli consensus path/to/.agents
pytest tests/
```

## Layout
- `agent/consensus.py` — the importable library (single source of truth).
- `meta/_i13_consensus.py` — the cascade entry point; delegates to the lib.
- `tests/test_agent.py`.

## Relationship to the other modules
`agent` attests to `i4`; `subagent` is the hosted variant; `constructor`
folds collapses; an agent's attestation is itself a collapse the consensus
root verifies.

## Provenance
I-13 is human-directed (David Lee Wise) + AI-co-authored (Hermes Agent,
Nous Research). AI co-creator credit is provenance, not derivation.

========================================================================
