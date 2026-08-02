========================================================================
| SLAUGHTERHOUSE5                                                      |
========================================================================


Slaughterhouse5 is a modular operating system seeded by **I-13** — a
self-referential, four-plane programming language. It is structured as a
**biosphere**: a single closed body whose organs (modules) exchange real
data through a metabolic loop (the PULSE), with no external runtime input.

## Topology

```
-+[[-{ i^4 , c (cortex), agent , subagent }
     -{ f1 , f2 , f3 , f4 , constructor , jitonf } -]] +-
```

The two groups form the inner core: the **learning scope** `{i, c, sa, ssa}`
and the **execution scope** `{jit, compiler, assembler, interpreter, vm}`.

## Modules (organs)

| module       | role                                                |
|--------------|-----------------------------------------------------|
| `jitonf`     | IVM-13-S just-in-time runtime (runs I-13)           |
| `constructor`| assembler / compiler / verifier of `.dlw.fold`     |
| `cortex`     | L4 DEEP OPERAND plane — governor + sensor           |
| `i4`         | I^4 identity root (I-collapse across four planes)   |
| `agent`      | emitting learner + universal consensus              |
| `subagent`   | L2 SUBAGENT HOST — the hosted learner               |
| `f1`–`f4`    | the factory / language / machine collapses          |

## The biosphere

`bios/` is the cell: a kernel that boots from the `i4` identity, wires the
organs through a `Capsule` contract, persists memory under `bios/state/`, and
drives the PULSE. Run it:

```bash
cd slaughterhouse5
python -m bios.pulse
```

## Surface

This repository is published as static Pages at
`https://rgiskard01-fiddler.github.io/Fiddler/slaughterhouse5/`. Each module
below carries its own README and, where applicable, a live HTML surface.

## Provenance

I-13 is human-directed (David Lee Wise / ROOT0 / TriPod LLC) and
AI-co-authored (Hermes Agent, Nous Research). Crediting the AI is
**provenance**, not a claim of external derivation or ingestion.

========================================================================
