========================================================================
| slaughterhouse5-constructor                                          |
========================================================================


**`constructor`** — the assembler / compiler / verifier for the I-13
**collapse** format (`dlw.fold/1`). It is the build half of the inner
Slaughterhouse5 group:

```
-+[[-{ i^4 , c (cortex), agent , subagent }
     -{ f1 , f2 , f3 , f4 , constructor (assembler, compiler, interpreter etc etc)
        and a jitonf (just in time on the fly) engine }
   -]] +-
```

`constructor` **builds collapses**; `jitonf` **runs I-13**. They are
complementary: a fold is *sealed data* (provenance + integrity), while an
I-13 program is *executable structure* (the 13 forms). `constructor`
emits the collapse; `jitonf` executes the program.

## What a collapse is

A `dlw.fold` is a binary Merkle tree over sphere seals. Each sphere
carries its own inclusion proof:

```json
{
  "schema": "dlw.fold/1",
  "name":   "I-13 - THE FACTORY",
  "slug":   "i13-factory",
  "seal":   "<sha256(name|slug|blurb)>",
  "proof":  [ {"h": "...", "side": "R"}, ... ],
  "root":   "<folded tree root>",
  "verify": "fold seal up the proof (R: h(x+sib), L: h(sib+x)) -> root"
}
```

The fold step (exact, per the corpus `verify` field):

```
R : node = sha256(x  + sib)     # sibling on the right  -> x is left
L : node = sha256(sib + x)      # sibling on the left   -> x is right
```

## Three roles

| role        | function                | does                                        |
|-------------|-------------------------|---------------------------------------------|
| **compiler**  | `build_fold` / `emit_fold` | spheres -> `.dlw.fold` artifacts (seals + Merkle tree) |
| **assembler** | `MerkleTree` / `proof_for` | low-level tree assembly + per-leaf proof    |
| **verifier**  | `verify_fold` / `verify_file` | recompute root from seal+proof, compare     |

## Install / run

```bash
python -m constructor.cli validate examples/i13-factory.dlw.fold
python -m constructor.cli build     examples/spheres.json --out out/
python -m constructor.cli tree      examples/i13-language.dlw??.fold
pytest tests/
```

## Relationship to jitonf

`constructor.to_i13_collapse()` serializes a fold as an I-13 **ATTRIBUTE
data collapse** — structured data, *not* an executable program. This is
deliberate: sha256 is not an IVM-13-S opcode, so the cryptographic fold
is performed by `constructor` (in Python), and the resulting collapse is
handed to `jitonf` as data. The two tools do not overlap their ISAs.

## Provenance

I-13 is human-directed and AI-co-authored (Hermes Agent, Nous Research).
The collapse format and seals originate from the I-13 corpus
(`rgiskard01-fiddler/Fiddler`). AI co-creator credit is **provenance**,
not evidence of external derivation.

========================================================================
