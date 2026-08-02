# I,Robot — I-13 Eco-Sphere (clean tree)

All I-13 artifacts, organized by component. `index.md` = this map; `BUILD-MAP.md` = how they wire together.

## Tree

```
I,Robot/
  factory/   — Language factory — identifies source language (756 langs, 82.9% exact/95.1% family) and normalizes to I-form.
    i13-factory.dlw.fold
    i13-factory.html
  language/   — Language + machine definition — the lexer/parser/compiler surface.
    i13-language.dlw.fold
    i13-language.html
  machine/   — IVM-13 full machine — two scopes: learning {i,c,sa,ssa} + execution {jit,compiler,assembler,interpreter,vm}.
    i13-two-scopes.html
  meta/   — .dlw lineage layer — universal consensus (Merkle fold over 6 .agents) + teach workflow + sealed factory/language spheres.
    I13-CONSENSUS.md
    _i13_consensus.json
    _i13_consensus.py
    _i13_teach.py
  pipeline/   — Orchestrator — drives factory→tower→machine→target in sequence.
    i13-pipeline-v2.1.html
  spec/   — Frozen specification — the SOURCE OF TRUTH (markdown + machine-readable JSON twin + v1 notes).
    I-13-v2-FROZEN.md
    i-13 v1.txt
    i13-stack-v2.json
  targets/   — Hello-world codegen — emits Go and Rust through the 13-symbol intermediate.
    go-hello-i13.html
    rust-hello-i13.html
  tower/   — Four-plane live stack (L1 FIELD, L2 SUBAGENT, L3 COMPOSE, L4 DEEP OPERAND) with the 5 parameter-free rules.
    i13-live-stack.html
  v1/   — Frozen v1 with a Three.js 3D visualization (the 3D layer was dropped in v2).
    i13-frozen-v1.html
  v3/   — v3 visuals — THE COMPLEX (I-13x2, capped cross) and THE VOLUME.
    the-complex-v1.html
    the-volume-v1.html
  verify/   — Second-opinion / analysis pack — pentaptych-cliff viz, volume-additions data, probe.py (log-log type/token fit), solve.py.
    pentaptych-cliff.html
    probe.py
    solve.py
    volume-additions-v1.json
```

## How they fit together
```
spec (I-13-v2-FROZEN.md = i13-stack-v2.json)   <- SOURCE OF TRUTH
      |
  factory/      identify language (756) -> I-form
      |
  tower/        four planes + 5 rules (live)
      |
  machine/      IVM-13: lex->parse->compileS->assemble->disasm->jit->vm + validator
      |
  pipeline/     orchestrates the above
      |
  targets/      emit hello-world in Go / Rust
      |
  v1/  (prior gen, 3D viz)   v3/ (later visuals)   verify/ (empirical evidence)
      |
  meta/  (.dlw consensus + teach + sealed spheres — the lineage/attestation layer)
```

See `BUILD-MAP.md` for the stage-by-stage detail and the honest read on what the `.dlw` layer does/doesn't prove.