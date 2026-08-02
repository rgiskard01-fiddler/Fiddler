# slaughterhouse5-cortex

**`cortex`** — the **L4 DEEP OPERAND** plane and the *governor + sensor*
of the four-plane I-13 stack. It is the deepest module in the inner
Slaughterhouse5 group:

```
-+[[-{ i^4 , c (cortex), agent , subagent }
     -{ f1 , f2 , f3 , f4 , constructor , jitonf } -]] +-
```

`cortex` is the only scope permitted to touch L4. Its spec role, in
`I,Robot/hermes.i13`:

> a feature is advice, a veto is a wall
> the cortex still verifies at the end

## The four-plane stack (verbatim from the baseline)

| plane | name            | nodes   | address bits |
|-------|-----------------|---------|--------------|
| L1    | FIELD           | 395162  | 19           |
| L2    | SUBAGENT HOST   | 209068  | 18           |
| L3    | COMPOSE         |  38742  | 16           |
| **L4**| **DEEP OPERAND**|  **6662** | **13**     |

`cortex` builds a deterministic stand-in operand table over the real
13-bit L4 address space (0..6661). The **address space and governance
are exact**; the individual operand *payloads* are a reproducible
placeholder because the 6662 trained weights are not stored as text in
the corpus.

## Two roles

### GOVERNOR — the five parameter-free rules
| rule          | behaviour (hard wall)                                  |
|---------------|--------------------------------------------------------|
| `veto`        | forbid the wrong closer                                |
| `-I`          | supply the owed closer                                 |
| `depth`       | refuse a plane already paid for                        |
| `idempotence` | a no-op cannot repeat (`I am I`)                       |
| `address`     | the substrate writes the 13-bit position               |

Rule reach (per 1,000 nodes, L1..L4) is carried from the baseline and
printed by `cortex planes`.

### SENSOR — cortex state fed back as features
The real empirical deltas from `v1#arch` / `v1#base`:
L2 mismatch `15.0 -> 0.6`, L1 stray-close `65.0 -> 1.0`. `cortex sense`
returns these as the feedback vector.

## Usage

```bash
python -m cortex.cli planes
python -m cortex.cli resolve 42
python -m cortex.cli veto --open FUNCTIONDEF --closer RETURN --expect FUNCTIONDEF:RETURN
python -m cortex.cli sense
python -m cortex.cli verify examples/veto-trace.json
python -m cortex.cli policy
pytest tests/
```

## Relationship to jitonf / constructor

* `jitonf` executes I-13 (the IVM-13-S runtime). `cortex` governs the
  *learning* scope (`i, c, sa, ssa`) that feeds it — a feature is
  advice, a veto is a wall.
* `constructor.to_i13_collapse` and `cortex.to_i13_policy` both emit
  I-13 **ATTRIBUTE data collapses** (data, not executable — sha256 is
  not an IVM-13-S opcode). The cortex performs the crypto/governance and
  hands the result to the executor as data.

## Provenance

I-13 is human-directed and AI-co-authored (Hermes Agent, Nous Research).
The plane counts, rule reach, and sensor deltas are drawn from the
unified baseline `I,Robot/hermes.i13`. AI co-creator credit is
**provenance**, not evidence of external derivation.
