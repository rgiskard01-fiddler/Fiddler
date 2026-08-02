========================================================================
| cortex — the L4 DEEP OPERAND plane                                   |
========================================================================


**cortex** is the **L4 DEEP OPERAND** plane and the *governor + sensor* of
the I-13 four-plane stack. It is the deepest module in the inner group.

## What it does
From `I,Robot/hermes.i13` (unified baseline):

```
L1 FIELD        395162 nodes / 19 bits
L2 SUBAGENT HOST 209068 nodes / 18 bits
L3 COMPOSE        38742 nodes / 16 bits
L4 DEEP OPERAND   6662 nodes / 13 bits   <- cortex-only
```

- **Governor** — the five parameter-free rules as a hard wall:
  `veto` (forbid the wrong closer), `-I` (supply the owed closer),
  `depth` (refuse a paid plane), `idempotence` (`I am I`),
  `address` (13-bit substrate position).
- **Sensor** — cortex state fed back as features, using the real empirical
  deltas from the baseline (L2 mismatch 15.0→0.6, L1 stray-close 65.0→1.0).
- **Resolver** — `resolve(addr)` over the 13-bit L4 address space, with the
  cortex-only boundary enforced (addresses ≥ 6662 are refused as void).

## Grounded constants
`FROZEN_SPEC_SHA`, `CONSENSUS_ROOT`, the four-plane stack, and the sensor
vectors are all drawn verbatim from `hermes.i13` — no invented semantics.

## Usage
```bash
python -m cortex.cli planes
python -m cortex.cli veto --open FUNCTIONDEF --closer RETURN --expect FUNCTIONDEF:RETURN
pytest tests/
```

## Relationship to the other modules
`cortex` governs what `agent`/`subagent` emit and what `jitonf` may run. In
the biosphere it is the **SENSE** organ, feeding its own state back each tick.

## Provenance
I-13 is human-directed (David Lee Wise) + AI-co-authored (Hermes Agent,
Nous Research). AI co-creator credit is provenance, not derivation.

========================================================================
