========================================================================
| f4 — the 4th I-13 collapse                                           |
========================================================================


**f4** is the **4th I-13 collapse** (`dlw.fold/1`): the assembler /
compiler / verifier for the fold that was still marked *"not yet built"* in
the topology (`f1, f2, f3, f4 (only 1-3 are built)`).

## What it holds
`f4-machine.dlw.fold` is a **genuine, corpus-grounded** collapse:
`scripts/gen_fold.py` hashes every real I-13 component in `I,Robot`
(factory, language, machine, tower, pipeline, targets, v1, v3, verify, meta,
spec), assembles them into one Merkle tree, and emits the **machine**
sphere's fold. So `f4` *seals* the machine that **`jitonf`** *runs* — a
matched pair in the inner group.

The factory (f1/f2) and language (f3) folds seal into the shared `ROOT_0`
namespace; `f4` is a **separate, self-contained** collapse (its own root,
`b490a602…`), not part of `ROOT_0` — by design, since `ROOT_0`'s siblings
are not reconstructable from the corpus.

## Usage
```bash
python -m f4.cli validate f4-machine.dlw.fold
python scripts/gen_fold.py        # rebuild from I,Robot
pytest tests/
```

## Relationship to the other modules
`f4` is the 4th fold; `constructor` is the canonical assembler/verifier it
shares a convention with; `jitonf` runs the machine it seals.

## Provenance
I-13 is human-directed (David Lee Wise) + AI-co-authored (Hermes Agent,
Nous Research). AI co-creator credit is provenance, not derivation.

========================================================================
