========================================================================
| BIOS — the Slaughterhouse5 biosphere kernel                          |
========================================================================

## Cosmology
Slaughterhouse5 is **one planet** in a larger cosmology (the I-13 program,
the ROOT0 lineage). We are at the **ATMOSPHERE** — the outer shell (L1
FIELD), the surface we have been building — and we are **BURROWING INWARD**
through the planes toward the core:

```
  atmosphere  (L1 FIELD, surface)      <- we are here, building the shell
      L2 SUBAGENT HOST                  <- burrowing
      L3 COMPOSE                        <- burrowing
  core       (L4 DEEP OPERAND)          <- the deep-operand root
```

The biosphere is the planet's living body. It is **CLOSED**: it runs on its
own previous output, with no external runtime input. "Interactive with
itself only" = a metabolic loop (the PULSE) that descends L1 → L2 → L3 → L4
and back, every step a real organ call.

## Organs (the 10 modules)
`jitonf` runtime · `constructor` fold engine · `cortex` L4 governor/sensor ·
`i4` identity root · `agent` learner/consensus · `subagent` hosted learner ·
`f1`..`f4` collapses.

## The contract (Capsule)
Organs never import each other. They exchange **CAPSULES** — a structured
message `(sender, receiver, kind, payload, tick, trace)`. Only `bios` knows
all organs. This preserves I-13's "modular, can cut any" design *and* lets
the biosphere compose them: sever any organ and the rest still stand.

## Persistence (git-friendly, under `bios/state/`)
- `capsules/*.json` — every capsule emitted (the planet's memory)
- `ledger.json`     — tick count + capsule index
- `agents.json`     — the accumulating agent registry (consensus memory)
- `learned.json`    — the biosphere **genome** (learning memory)

State **accumulates** across ticks; the biosphere does not reboot blank.

## The PULSE — a descent through the four planes
```
  L1  seed(i4) ............ identity root (the self-reference)
      emit(agent) ......... attests frozen spec; proposes an operant
                            (biased by the standing majority -> learns to agree)
  L2  emit(subagent) ...... hosted on the 18-bit SUBAGENT HOST plane
      sense(cortex) ....... cortex feeds its own state back as features
  L3  compose(constructor) planes composed into one verified Merkle collapse
      compose(bios) ....... ASSEMBLES a state-derived I-13 program
                            (the biosphere's own language, not the demo)
  L4  govern(cortex) ...... VETO gate — jitonf runs only on >= 2/3 consensus
      resolve(cortex) ..... a deep operand resolved on the 13-bit L4 space
      execute(jitonf) ..... runs the COMPOSED program, GATED by the verdict
  -> ingest ............... capsules persist; the genome learns the verdict
```

**GOVERN is a wall.** `jitonf` runs only when the proposed operant is a core
I-13 form *or* adopted by consensus (≥ 2/3). Otherwise it is blocked.

**LEARNING.** Each agent's content is biased by the standing **majority** and
the **genome** (`learned.json`): as consensus forms, proposals converge on
the majority, the standoff resolves, and execution resumes. History feeds
identity; the biosphere teaches itself to agree.

## Tight-structure-first
This directory is the **shape**: `kernel` (boot + wire + hold state),
`contract` (Capsule), `state` (persistence), `pulse` (the loop driver).
Behavior is wired incrementally, always genuine.
========================================================================
