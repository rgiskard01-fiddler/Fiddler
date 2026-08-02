# slaughterhouse5-f4

**`f4`** — the **4th I-13 collapse** (`dlw.fold/1`): the assembler /
compiler / verifier for the fold that was still marked *"not yet built"*
in the topology (`f1, f2, f3, f4 (only 1-3 are built)`).

Part of the I-13 program, inside the Slaughterhouse5 OS:

```
-+[[-{ i^4 , c (cortex), agent , subagent }
     -{ f1 , f2 , f3 , f4 , constructor , jitonf } -]] +-
```

## What it does

`f4` is a self-contained **fold engine** that mirrors the `constructor`
module's Merkle convention — the exact `R: h(x+sib), L: h(sib+x)`
**hex-string** concat that matches the sealed corpus folds. It produces and
verifies `dlw.fold/1` collapses.

The shipped collapse (`f4-machine.dlw.fold`) is **genuine and corpus-grounded**:
`scripts/gen_fold.py` hashes every real I-13 component in `I,Robot`
(factory, language, machine, tower, pipeline, targets, v1, v3, verify,
meta, spec), assembles them into one Merkle tree, and emits the **machine**
sphere's fold. So `f4` *seals* the machine that **`jitonf`** *runs* — the two
inner-group modules are a matched pair.

> The factory (f1/f2) and language (f3) folds seal into the shared
> `ROOT_0` namespace. `f4` is a **separate, self-contained** collapse
> (its own root, `b490a602…`), not part of `ROOT_0` — by design, since the
> `ROOT_0` siblings are not reconstructable from the corpus.

## Layout

* `f4/fold.py` — `Sphere`, `MerkleTree`, `build_fold`, `emit_fold`,
  `verify_fold`, `verify_file` (the fold engine).
* `f4/cli.py` — `validate`, `info`, `build`.
* `scripts/gen_fold.py` — regenerate `f4-machine.dlw.fold` from the corpus.
* `f4-machine.dlw.fold` — the committed 4th collapse (verifiable).
* `f4-components.json` — every component's fold, for reference.
* `tests/test_fold.py` — 6 tests (incl. verifying the real fold + the
  canonical factory fold via f4's engine).

## Usage

```bash
python -m f4.cli validate f4-machine.dlw.fold
python -m f4.cli info f4-machine.dlw.fold
python -m f4.cli build examples/spheres.json --out out/
python scripts/gen_fold.py        # rebuild from I,Robot
pytest tests/
```

## Relationship to the other modules

* `constructor` is the canonical assembler/verifier; `f4` is a sibling
  fold engine with the same convention (the fold format is shared).
* `jitonf` *runs* the machine; `f4` *seals* it — paired members of the
  inner group.
* `f1`/`f2`/`f3` carry the factory/language folds and verify with this same
  engine (cross-checked in the test suite).

## Provenance

I-13 is human-directed and AI-co-authored (Hermes Agent, Nous Research).
The collapse is built from the real `I,Robot` corpus. AI co-creator credit
is **provenance**, not evidence of external derivation.
