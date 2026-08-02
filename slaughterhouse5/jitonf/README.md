========================================================================
| jitonf — IVM-13-S runtime                                            |
========================================================================


**jitonf** is the **IVM-13-S** (I-13 Structured Virtual Machine) runtime —
the *execution* half of the inner Slaughterhouse5 group. It is the only
scope permitted to *run* I-13 programs.

## What it does
- **Lex / parse / compile** I-13 source into a structured program (S-tree).
- **Execute** on a stack VM (opcodes: `LD, ST, PUSH, ADD, SUB, MUL, EQ, LT,
  GT, AND, OR, NOT, JZ, JNZ, RET`) with the law **net = binds − k** (stack
  produced minus stack consumed).
- **JIT** — a just-in-time path that matches the VM result exactly.
- **Validate** — a linear, non-executing walker that rejects faults
  (e.g. an injected `RET` on an empty stack) without a control-flow graph.

## Grounded in
The reference lexer/parser/evaluator was ported faithfully from the I-13
machine reference (`machine/i13-two-scopes.html`); no semantics were invented.

## Usage
```bash
python -m jitonf.cli run "I x <- 3 ; I y <- 4 ; I sum <- x + y ;"
python -m jitonf.cli validate examples/demo.i13
pytest tests/
```

## Layout
- `jitonf/ivm13s.py` — lexer, parser, compiler, validator, VM, JIT.
- `jitonf/cli.py` — `run`, `validate`, `compile`.
- `examples/demo.i13`, `tests/test_demo.py`.

## Relationship to the other modules
`jitonf` *runs* what `constructor` folds and `cortex` governs. In the
biosphere PULSE it is the **EXECUTE** organ: it genuinely runs I-13 each
tick.

## Provenance
I-13 is human-directed (David Lee Wise) + AI-co-authored (Hermes Agent,
Nous Research). AI co-creator credit is provenance, not derivation.

========================================================================
