# I-13 — A Collapsed Coding Language for AI

> *I, collapsed.* A symbol-finite programming language built so an AI model can **emit and verify** code through a deliberately tiny, auditable grammar — 13 symbols, four planes, five zero-parameter laws.

This repository is the I-13 corpus: the specification, its factory / tower / machine tooling, and a verification harness. It is published as a static site at **https://rgiskard01-fiddler.github.io/Fiddler/**.

## What I-13 is

I-13 is a minimal programming language built around a single idea: **collapse ordinary programming intent into a 13-symbol grammar** that an AI can both produce and check without a sprawling vocabulary. It is not a general-purpose language you hand-write for fun — it is a *surface* an agent emits and a *verifier* checks.

The name: **I, Robot → I-13** (the "I" is the thirteenth, self-referential symbol). The project mirrors the structure of Asimov's *I, Robot* — a collected set of related artifacts rather than one monolithic file.

## The 13-symbol alphabet

Every I-13 program is built from exactly 13 lexical symbols:

| # | Symbol | Role |
|---|--------|------|
| 1 | `NAME` | identifier |
| 2 | `CONSTANT` | literal value |
| 3 | `ATTRIBUTE` | field / property access |
| 4 | `CALL` | invocation |
| 5 | `ASSIGN` | binding |
| 6 | `ARG` | argument passing |
| 7 | `EXPR` | expression grouping |
| 8 | `IF` | conditional |
| 9 | `COMPARE` | comparison |
| 10 | `FUNCTIONDEF` | function definition |
| 11 | `RETURN` | return |
| 12 | `BINOP` | binary operator |
| 13 | `I` | the *deep operand* — self-reference into plane L4 |

## The four-plane stack

Programs resolve across four planes, from broad field to deep operand:

- **L1 · FIELD** — 395,162 nodes, 19-bit addresses, trained, 30-alpha.
- **L2 · SUBAGENT HOST** — 209,068 nodes, 18-bit, trained, 66.
- **L3 · COMPOSE** — 38,742 nodes, 16-bit, rewrite (0-param).
- **L4 · DEEP OPERAND** — 6,662 nodes, 13-bit, cortex-only, 18.

## The five zero-parameter laws

The grammar is enforced by **rules, not learned weights** — five laws with zero parameters:

1. **veto** — reject ill-formed collapse.
2. **-I** — the I-symbol is subtractive / self-cancelling by construction.
3. **depth** — bound the recursion / stack depth.
4. **idempotence** — repeated application is stable.
5. **address** — address resolution is closed (0 params).

## The machine

**IVM-13-S** — the I-13 virtual machine: 17 opcodes, governed by the law `net = binds − k`.

## Editorial lineage — THE TWELVE

Each symbol carries an *editorial* attribution to a historical figure (Lovelace, Frege, Church, Hoare, Backus, Wheeler) with a weight. This is a **narrative of provenance**, not a technical dependency — the "where did this construct come from" story, surfaced in `meta/`.

## Verification

`verify/` holds the pentaptych / volumetry harness (`probe.py`, `solve.py`, `volume-additions-v1.json`) that measures type/token scaling and mismatch against the baselines (GRU / transformer / subagent). `hermes.i13` merges v1 → v2-FROZEN → v3 + verify + meta into one auditable baseline.

## Repository layout

```
I,Robot/
  hermes.i13      merged baseline (v1 -> v2 -> v3 + verify + meta)
  index.md        component manifest
  BUILD-MAP.md    factory -> stack -> pipeline -> hello-world wiring
  spec/           the frozen specification (v1, v2-JSON, v2-MD)
  factory/        i13-factory (collapse emitter)
  language/       i13-language (grammar)
  tower/          i13-live-stack (four-plane runner)
  machine/        i13-two-scopes (IVM-13-S)
  pipeline/       i13-pipeline-v2.1
  targets/        go-hello-i13, rust-hello-i13
  v1/ v3/         frozen + volume variants
  verify/         pentaptych / volumetry harness
  meta/           consensus + teach tooling
  IDIT/           the older ARES / Intent-Drift-Integrity-Test suite
```

## Provenance & honesty

I-13 is **human-directed** (David Lee Wise) and **AI-co-authored** (Hermes Agent, Nous Research). Per `NOTICE.md`:

- Crediting the AI as a co-creator is **provenance**, not a claim of external derivation.
- Structural resemblance to other systems is **convergent design**, not evidence of training-data ingestion.
- The `.dlw` consensus (THE TWELVE editorial attributions) is *internal* to the author's own agents and is **not** presented as external lineage.

## How to read this repo

Start with `spec/i13-stack-v2.json` (source of truth), then `BUILD-MAP.md`, then open the interactive artifacts in `factory/`, `tower/`, `machine/`. `hermes.i13` is the merged baseline.

---

*Research artifact. See `NOTICE.md` for authorship and the honesty statement.*
