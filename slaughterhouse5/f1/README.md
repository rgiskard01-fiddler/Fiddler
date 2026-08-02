========================================================================
| f1 — factory + language collapse                                     |
========================================================================


**f1** carries the **factory** and **language** I-13 collapses
(`dlw.fold/1`): the sealed Merkle folds of THE FACTORY and THE LANGUAGE.

## What it holds
- `f1-factory.dlw.fold` — THE FACTORY collapse (seal `8d6c265f…`, folds to
  the shared `ROOT_0` `549f12…`).
- `f1-language.dlw.fold` — THE LANGUAGE collapse (seal `788ff9e5…`, folds to
  the same `ROOT_0`).

Both verify against their sealed root using the corpus convention
`R: h(x+sib), L: h(sib+x)` (hex-string concat) — the same engine `constructor`
implements and the biosphere's **GOVERN+FOLD** step uses.

## Usage
```bash
python -m f4.cli validate f1-factory.dlw.fold   # shares the f4 fold engine
```

## Relationship to the other modules
`f1` is the factory/language seed material; `f2`/`f3` carry the individual
factory/language folds; `f4` is the 4th collapse (machine); `constructor`
verifies and assembles all of them.

## Provenance
I-13 is human-directed (David Lee Wise) + AI-co-authored (Hermes Agent,
Nous Research). AI co-creator credit is provenance, not derivation.

========================================================================
