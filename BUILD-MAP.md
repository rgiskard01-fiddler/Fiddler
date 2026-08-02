# I,Robot — I-13 Build Map

How the gathered I-13 artifacts wire together: data root -> factory -> tower ->
machine -> pipeline -> target, plus the `.dlw` meta/lineage layer.

## Source of truth
`i13-stack-v2.json` is the FROZEN v2 spec in machine-readable form — same
sha256 (`64881ebf…`) as `I-13-v2-FROZEN.md`, so the `.md` and `.json` are two
renderings of one artifact. Everything else either *visualizes* it (the HTML
demos) or *consumes/attests* it (the consensus layer).

## Pipeline

```
 i13-stack-v2.json  (FROZEN v2, sha256 64881eb…)   <- SOURCE OF TRUTH
                       planes · rules · machine · factory · twelve
                                  |
   +------------------------------+-------------------------------+
   | FACTORY   i13-factory.html                                   |
   |   lex -> parse -> compile -> PDA(stack) -> depth/balance/legal|
   |   756 langs indexed · 82.9% exact / 95.1% family · quantile  |
   +------------------------------+-------------------------------+
                                  v
   +------------------------------+-------------------------------+
   | TOWER (live)  i13-live-stack.html                            |
   |   L1 FIELD · L2 SUBAGENT · L3 COMPOSE · L4 DEEP OPERAND     |
   |   c(sa()) features · Cortex(sensor) · 5 rules               |
   +------------------------------+-------------------------------+
                                  v
   +------------------------------+-------------------------------+
   | MACHINE   i13-two-scopes.html                                |
   |   scope1 {i,c,sa,ssa}  |  scope2 {jit,compiler,assembler,   |
   |                          interpreter,vm}                      |
   |   lex -> parse -> compileS -> assemble -> disasm -> JIT -> VM|
   |   validator (validateS/validateOne) · regions/planes        |
   +------------------------------+-------------------------------+
                                  v
   +------------------------------+-------------------------------+
   | PIPELINE  i13-pipeline-v2.1.html   (orchestrator / show)     |
   +------------------------------+-------------------------------+
                                  v
   +------------------------------+-------------------------------+
   | TARGET   go-hello-i13.html · rust-hello-i13.html            |
   |   emit hello-world in Go / Rust via the 13-symbol intermediate|
   +--------------------------------------------------------------+

 META / .dlw LAYER (lineage watch)
   _i13_consensus.py   -> Merkle fold over agent attestations (main/merkle/_sha)
   _i13_consensus.json -> 6 agents, all attest same spec, consensus_root Merkle
   I13-CONSENSUS.md    -> narrative of the universal consensus
   _i13_teach.py       -> teach workflow that feeds I-13 to agents
   i13-*.dlw.fold      -> sealed spheres (factory idx4, language idx3)
                         anchor 0ROOT.AI//THE-FOLD · David Lee Wise (ROOT0) · AVAN
```

## Stage-by-stage
- **Factory** (`i13-factory.html`, title "factory production pipeline"): lexer,
  parser, compiler, a PDA (pushdown automaton = the stack discipline), plus
  `corpus`/`depth`/`balance`/`legal` checks. This is the 756-language identifier
  from the spec — it reads source, identifies the language (82.9% exact /
  95.1% family) by the per-corpus quantile law, and normalizes to the I-form.
- **Tower live** (`i13-live-stack.html`, "the whole stack, live", 290 KB): the
  four planes running — `Cortex` (the sensor/governor), `address` (the address
  rule), `feats` (the c(sa()) features), `score`/`mask`. This is where the five
  parameter-free rules are exercised on live input.
- **Two scopes** (`i13-two-scopes.html`): the FULL machine. Title decodes as
  two scopes — **scope 1 `{i, c, sa, ssa}`** = the *learning* side (the planes /
  features), **scope 2 `{jit, compiler, assembler, interpreter, vm}`** = the
  *execution* side. Pipeline: `lex -> parse -> compileS` (structured) ->
  `assemble -> disasm -> jit -> vm`, with `validateS`/`validateOne` as the
  one-pass validator (no execution, no CFG — per the spec's `validate` law).
- **Pipeline v2.1** (`i13-pipeline-v2.1.html`, "the full pipeline"): a thin
  orchestrator/show layer (`onclick`/`show`) that drives the stages above in
  sequence. It is the integration surface, not new machinery.
- **Targets** (`go-hello-i13.html`, `rust-hello-i13.html`): "hello, world —
  Go/Rust through I-13". They take the 13-symbol intermediate and emit valid
  Go / Rust — the proof that the I-13 intermediate can target real languages.
- **v1 frozen** (`i13-frozen-v1.html`): the v1 artifact, but its script is a
  Three.js 3D scene (`build3d`/`boot3d`, AxisHelper, WebGLRenderTarget…). The
  3D visualization was dropped by v2 — v2 is text/markup only.

## The `.dlw` meta layer (your lineage watch)
This is the part most relevant to the `.dlw` signal:
- `_i13_consensus.py` (defs `_sha`, `merkle`, `main`; imports only `math`,
  `os`) builds a **Merkle fold** over every `.agent` that *learned I-13* and
  *proposed a language extension*. Its doc says it is "run by the daily cascade
  (`_cascade.py`)".
- `_i13_consensus.json` (`i13-universal-consensus`, 2026-08-01): `agents_count:
  6`, `all_attest_same_spec: true`, `consensus_root` = Merkle fold over the 6
  attestations. `extended_alphabet` = 13 symbols (the 12 operants + `I`).
  `proposal_tally`: LAMBDA 2, AWAIT 1, IMPORT 1, SLICE 1, SPAWN 1;
  `adopted_extensions: 0` (supermajority threshold 4 not reached on any). So the
  language stayed at 13 symbols — no extension was adopted.
- `i13-*.dlw.fold` (`schema dlw.fold/1`, `world "II"`, `kind "sphere"`): your
  seal format. `algo: sha256(name|slug|blurb) + sha256 merkle-fold`,
  `anchor: 0ROOT.AI//THE-FOLD//4096->0//David Lee Wise (ROOT0)//with AVAN`.
  Factory sphere = index 4, language sphere = index 3.

### What this layer does and does NOT prove
It proves, cryptographically (Merkle fold), that **your own six `.agents`**
learned I-13 and attest to the same frozen spec, and that you sealed the
factory/language spheres under your ROOT0/AVAN anchor. That is an *internal*
consensus — it does **not** by itself establish that an *external* system
(Hermes, Opus 4.6) derives from your work. For the `.dlw` watch, the honest
read: this is strong evidence of *your* agents' convergence on I-13, not of
descent from your work into outside models. An external-derivation claim would
still need an artifact-to-artifact chain outside this folder.

## Gaps / not yet captured
- `_cascade.py` is referenced (runs the daily consensus) but is **not** in the
  gathered set — only its consensus output (`_i13_consensus.*`) is here.
- `_i13_teach.py` (32 KB, defs `_sha/_esc/_e3/_erw`, imports `json`) was not
  fully read; it is the teach-side counterpart to consensus but its internals
  are unparsed here.
- `i13 v3.zip` / `i13-second opinion.zip` are packed; v3 is not unpacked.
- v1's Three.js 3D viz is present only as the frozen HTML; the geometry/data
  behind it isn't separately captured.
