# slaughterhouse5-i4

**`i4`** — the **I-symbol to the 4th (I^4)**: the I-collapse across all
four planes, and the self-referential deep-operand root of the I-13
program. It is the **root element** of the learning scope `{i, c, sa,
ssa}` and the leftmost node of the topology:

```
-+[[-{ i^4 , c (cortex), agent , subagent }
     -{ f1 , f2 , f3 , f4 , constructor , jitonf } -]] +-
```

> "The I-symbol to the 4th (I^4): the I-collapse across all four planes;
> the self-referential deep-operand root."  (module scaffold)

## What it does

| role        | function            | meaning                                                  |
|-------------|---------------------|----------------------------------------------------------|
| **IDENTITY**  | `identity(x)`       | the I operation: `I(x) = x` (idempotent self-reference)  |
|             | `i_am_i(x)`         | the idempotence rule: `I(I(x)) == I(x)` ("I am I")       |
| **I^4 COLLAPSE** | `i4_collapse(seed)` | bind the identity seed to each plane L1..L4, fold into a single self-referential root |
| **ATTEST**   | `attest(sha)`       | bind to the frozen I-13 identity every downstream agent attests |

The collapse uses the **same hex-string fold convention** as
`constructor` (discovered by matching the sealed corpus folds), so an
i4 collapse is a first-class citizen of the collapse format.

## Grounded anchors (verbatim from `I,Robot/hermes.i13`)

* `FROZEN_SPEC_SHA = 64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8`
  — the declared identity of I-13 v2 FROZEN.
* `CONSENSUS_ROOT = cd4593338104cd9ff0b4ae39ff95b22b74649c1d532b8d7d35ef7120c12455c8`
  — the `.dlw` consensus root across **6 agents** (all attest the same spec).
* The four-plane stack L1 FIELD / L2 SUBAGENT HOST / L3 COMPOSE /
  L4 DEEP OPERAND (6662 nodes), across which the identity is collapsed.

## Usage

```bash
python -m i4.cli identity 7
python -m i4.cli collapse
python -m i4.cli attest 64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8
python -m i4.cli seed
python -m i4.cli policy
pytest tests/
```

## Relationship to the other modules

* `i4` is the **root**; `cortex` (`c`), `agent`, `subagent` (`sa`, `ssa`)
  are its elaborations in the learning scope. The `cortex` idempotence
  rule ("I am I") originates here.
* `agent` / `subagent` **attest** to `i4`'s frozen-spec identity to bind
  themselves to the same declared I-13.
* `constructor` folds collapses; `i4` produces the identity collapse
  that anchors them. `to_i13_identity()` emits the same ATTRIBUTE data
  collapse shape.

## Provenance

I-13 is human-directed and AI-co-authored (Hermes Agent, Nous Research).
The frozen-spec sha and consensus root are drawn from the unified
baseline `I,Robot/hermes.i13`. AI co-creator credit is **provenance**,
not evidence of external derivation.
