========================================================================
| slaughterhouse5-subagent                                             |
========================================================================


**`subagent`** — the **L2 SUBAGENT HOST** plane (18-bit, trained, 66): the
**hosted** I-13 learner. It is the `sa` element of the learning scope
`{i, c, sa, ssa}`.

Part of the I-13 program, inside the Slaughterhouse5 OS:

```
-+[[-{ i^4 , c (cortex), agent , subagent }
     -{ f1 , f2 , f3 , f4 , constructor , jitonf } -]] +-
```

## What it does

A subagent is an **agent** (it attests the frozen I-13 spec and proposes a
deterministic operant beyond THE TWELVE — see the `agent` module) *plus* a
**hosting layer**: it is bound to an **18-bit L2 host address** (0..262143)
within the L2 SUBAGENT HOST plane, whose trained alphabet has **66
symbols**. That hosting binding is what makes it `sa` rather than a bare
`agent`.

The `verify_host()` method is the cortex-style boundary check: a subagent is
legitimately hosted only if its L2 address is in range, its host symbol is
in the L2 alphabet, and it attests the frozen I-13 spec.

This module is self-contained (it re-declares the shared consensus
primitives) so it can be **cut** independently, exactly as the I-13 design
intends. Its behaviour mirrors `agent`; the hosting layer is the difference.

## Grounded constants (verbatim from the baseline)

* L2 SUBAGENT HOST: **209068 nodes / 18 bits**; address space 0..262143.
* Host alphabet size: **66** (the trained L2 alphabet). The first 25 entries
  are the real I-symbols — THE_TWELVE + `"I"` + the 12 candidate operants —
  and the remaining 41 are deterministic host glyphs (`H00`…) standing in
  for the trained L2 weights (not stored as text in the corpus).
* `FROZEN_SPEC_SHA = 64881ebf…` (== `i4` / `agent` anchor).

## Layout

* `subagent/subagent.py` — `SubAgent` (attest + propose + host), `verify_host`,
  `to_i13_host`.
* `subagent/cli.py` — `host`, `propose`, `verify`, `planes`, `policy`.
* `tests/test_subagent.py` — 8 tests.

## Usage

```bash
python -m subagent.cli host "subagent payload"
python -m subagent.cli planes
python -m subagent.cli verify "subagent payload"
python -m subagent.cli policy "subagent payload"
pytest tests/
```

## Relationship to the other modules

* `agent` is the bare learner; `subagent` adds L2 hosting.
* `i4` supplies the frozen-spec identity both attest to.
* `cortex` (`c`) is the governor; `subagent` (`sa`) is hosted under its L2.
* `to_i13_host()` emits the same ATTRIBUTE data-collapse shape as
  `constructor` / `cortex` / `i4`.

## Provenance

I-13 is human-directed and AI-co-authored (Hermes Agent, Nous Research).
The plane counts and frozen-spec sha are drawn from the unified baseline
`I,Robot/hermes.i13`. AI co-creator credit is **provenance**, not evidence
of external derivation.

========================================================================
