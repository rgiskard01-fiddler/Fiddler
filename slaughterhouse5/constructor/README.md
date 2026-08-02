========================================================================
| constructor — collapse assembler / compiler / verifier               |
========================================================================


**constructor** is the assembler, compiler, and verifier for the I-13
**collapse** format (`dlw.fold/1`) — the build half of the inner
Slaughterhouse5 group. `jitonf` *runs* I-13; `constructor` *seals* it.

## What it does
- **Compiler** — `build_fold` turns spheres (name/slug/blurb) into
  `.dlw.fold` artifacts: a leaf seal `sha256(name|slug|blurb)` folded into a
  Merkle tree.
- **Assembler** — `MerkleTree` + `proof_for` build the per-leaf proof.
- **Verifier** — `verify_fold(seal, proof, root)` recomputes the root with
  the corpus convention `R: h(x+sib), L: h(sib+x)` (hex-string concat — the
  exact rule the sealed factory/language folds use).

## Grounded in the corpus
The real `factory` and `language` folds in this repo **verify** against their
sealed root (`549f12…`) using this engine — a hard, reproducible check.

## Usage
```bash
python -m constructor.cli validate factory/i13-factory.dlw.fold
python -m constructor.cli build examples/spheres.json --out out/
pytest tests/
```

## Layout
- `constructor/fold.py` — `MerkleTree`, `build_fold`, `verify_fold`.
- `constructor/cli.py` — `validate`, `build`, `info`.
- `factory/`, `language/`, `pipeline/` — real I-13 collapse HTML + folds.

## Relationship to the other modules
The folds it produces are what `jitonf` runs and what the biosphere's
**GOVERN+FOLD** step builds and verifies each tick.

## Provenance
I-13 is human-directed (David Lee Wise) + AI-co-authored (Hermes Agent,
Nous Research). AI co-creator credit is provenance, not derivation.

========================================================================
