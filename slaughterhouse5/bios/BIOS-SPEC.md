========================================================================
| BIOS — the Slaughterhouse5 biosphere kernel                          |
========================================================================


## Cosmology
Slaughterhouse5 is **one planet** in a larger cosmology (the I-13 program,
the ROOT0 lineage). We are at the **ATMOSPHERE** — the outer shell (L1
FIELD), the surface we have been building — and we are **BURROWING inward**
through the planes toward the core:

```
  atmosphere  (L1 FIELD, surface)      <- we are here, building the shell
      L2 SUBAGENT HOST                  <- burrowing
      L3 COMPOSE                        <- burrowing
  core       (L4 DEEP OPERAND)          <- the deep-operand root
```

The biosphere is the planet's living body. It is **CLOSED**: it runs on its
own previous output, with no external runtime input. "Interactive with
itself only" = a metabolic loop (the PULSE) in which the organs pass real
I-13 data to one another.

## Organs (the 10 modules, already built)
`jitonf` runtime · `constructor` fold engine · `cortex` L4 governor/sensor ·
`i4` identity root · `agent` learner/consensus · `subagent` hosted learner ·
`f1`..`f4` collapses.

## The contract (Capsule)
Organs never import each other. They exchange **CAPSULES** — a structured
message `(sender, receiver, kind, payload, tick, trace)`. Only `bios` knows
all organs. This preserves I-13's "modular, can cut any" design *and* lets
the biosphere compose them: sever any organ and the rest still stand.

## Persistence
State lives in-repo under `bios/state/` as transparent files:
- `capsules/*.json` — every capsule emitted (the planet's memory)
- `ledger.json` — tick count + capsule index

Git-friendly: the biosphere's history is version-controlled. State
**accumulates** across ticks (the biosphere does not reboot blank).

## The PULSE (one metabolic tick)
```
seed(i4) -> emit(agent) -> govern(cortex + consensus)
         -> fold(constructor) -> execute(jitonf) -> ingest -> loop
```
Each step is a real organ call — real fold verification, real consensus,
real IVM execution — never simulated.

## Tight-structure-first
This directory is the **shape**: `kernel` (boot + wire + hold state),
`contract` (Capsule), `state` (persistence), `pulse` (the loop driver).
Behavior is wired incrementally, always genuine.

========================================================================
