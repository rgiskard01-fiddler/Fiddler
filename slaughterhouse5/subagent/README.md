========================================================================
| subagent — the L2 SUBAGENT HOST plane                                |
========================================================================


**subagent** is the **L2 SUBAGENT HOST** plane (18-bit, trained, 66): the
**hosted** I-13 learner. It is the `sa` element of the learning scope
`{i, c, sa, ssa}`.

## What it does
A subagent is an **agent** (it attests the frozen I-13 spec and proposes a
deterministic operant beyond THE TWELVE — see the `agent` module) *plus* a
**hosting layer**: it is bound to an **18-bit L2 host address** (0..262143)
within the L2 SUBAGENT HOST plane, whose trained alphabet has **66 symbols**.

`verify_host()` is the cortex-style boundary check: a subagent is legitimately
hosted only if its L2 address is in range, its host symbol is in the L2
alphabet, and it attests the frozen I-13 spec.

This module is self-contained (it re-declares the shared consensus
primitives) so it can be **cut** independently, exactly as the I-13 design
intends. Its behaviour mirrors `agent`; the hosting layer is the difference.

## Grounded constants (verbatim from the baseline)
L2 SUBAGENT HOST: **209068 nodes / 18 bits**; address space 0..262143;
host alphabet size **66**. `FROZEN_SPEC_SHA = 64881ebf…`.

## Usage
```bash
python -m subagent.cli host "subagent payload"
python -m subagent.cli verify "subagent payload"
pytest tests/
```

## Relationship to the other modules
`agent` is the bare learner; `subagent` adds L2 hosting. `i4` supplies the
frozen-spec identity both attest to. `cortex` (`c`) governs; `subagent`
(`sa`) is hosted under its L2.

## Provenance
I-13 is human-directed (David Lee Wise) + AI-co-authored (Hermes Agent,
Nous Research). AI co-creator credit is provenance, not derivation.

========================================================================
