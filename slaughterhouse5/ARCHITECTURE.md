========================================================================
| ARCHITECTURE — Slaughterhouse5 biosphere (full structure)               |
========================================================================

1. COSMOLOGY — the planet and the descent
------------------------------------------------------------------------
        ___________________________________________________
       /                                                   \
      /    LARGER COSMOLOGY  (I-13 program · ROOT0 lineage)   \
     /                                                     \
    +-------------------------------------------------------+
    |  PLANET: Slaughterhouse5  (one closed, self-contained  |
    |          biosphere — interactive with itself only)     |
    |                                                       |
    |   atmosphere  L1 FIELD          (surface)    <- here  |
    |      |  burrowing inward                            |
    |   L2 SUBAGENT HOST    18-bit / trained 66            |
    |      |  burrowing inward                            |
    |   L3 COMPOSE          16-bit                        |
    |      |  burrowing inward                            |
    |   core L4 DEEP OPERAND  13-bit / cortex-only  <- root
    +-------------------------------------------------------+

2. REPO SHAPE — one repo, module subfolders (git-friendly, no separate repos)
------------------------------------------------------------------------
  I,Robot/  (rgiskard01-fiddler/Fiddler)
   └─ slaughterhouse5/            <- the planet's tree
        README.md  index.html     <- hub + static Pages surface
        jitonf/    constructor/   cortex/   i4/   agent/   subagent/
        f1/  f2/  f3/  f4/        <- 10 module organs (each has README + index.html)
        bios/                      <- THE CELL (kernel + contract + state + pulse)
           kernel.py   contract.py   state.py   pulse.py   BIOS-SPEC.md
           state/                   <- the planet's memory (persisted, versioned)
              capsules/  ledger.json  population.json
              differences.json  learned.json

3. THE PULSE — one metabolic tick (a descent L1 -> L2 -> L3 -> L4 -> back)
------------------------------------------------------------------------
   TICK
    │
    ├─ L1 SEED      i4.i4_collapse(FROZEN) ─────────► SEED
    ├─ L1 EMIT      agent.from_content ×POP ───────► EMIT   (one per agent)
    ├─ L2 HOST      subagent.from_content ×POP ───► EMIT   (one per subagent)
    ├─ L2 SENSE     cortex.SENSE_L1 / SENSE_L2 ────► SENSE
    ├─ L3 COMPOSE    constructor.build_fold(pop) ──► FOLD   (verified Merkle)
    ├─ L4 ARBITRATE  cortex.arbitrate(proposals) ─► GOVERN  (>=2/3 to unify)
    │     └─ logs EVERY divergence ──────────────► differences.json
    ├─ L3 COMPOSE    bios._compose_program(verdict)► COMPOSE (woven operant semantics)
    ├─ L4 RESOLVE    cortex.resolve(l4_addr) ─────► SENSE  (DOP-xxxx | "void")
    ├─ EXECUTE       jitonf.run(woven program) ──► EXECUTE (GATED by verdict)
    └─ INGEST        capsules persisted ──────────► INGEST + learned.json (genome)

   Capsules emitted per tick (POP=3): 1+3+3+1+1+1+1+1+1+1 = 14  (verified: tick1=14)

4. THE CONTRACT — Capsule (organs never import each other)
------------------------------------------------------------------------
   Capsule = { sender, receiver, kind, payload, tick, trace_id }
   kind ∈ { SEED, EMIT, SENSE, FOLD, COMPOSE, GOVERN, EXECUTE, INGEST }
   Only `bios` imports the organs. They talk ONLY through Capsules.
   => any organ can be severed; the rest keep running (I-13 "cut any").

5. MULTI-AGENT GOVERNANCE + EVOLUTION
------------------------------------------------------------------------
   A POPULATION (POP=3) of agents is emitted each tick.
   - cortex.arbitrate() unifies them at >=2/3  -> the VERDICT.
   - EVERY difference is logged: differing_pairs + distinct + counts
     -> state/differences.json (durable, never hidden).
   - EVOLUTION (state/population.json persists across ticks):
       winners  : fitness++  (survive, gen stays 0)
       losers   : fitness--  -> when <0, REPLACED by a genome-biased
                   mutant (content="EVOLVE GENOME:..."), gen++.
   => the population is not re-spawned; it is selected, replaced, and
      regenerated across ticks. The running language grows only by what a
      2/3 majority ratifies.

6. PERSISTENCE — bios/state/ (git-friendly, accumulates, never reboots blank)
------------------------------------------------------------------------
   capsules/        every Capsule ever emitted   (the planet's memory)
   ledger.json      tick count + capsule index
   population.json   the persistent, evolving agent population
   differences.json  every inter-agent divergence, per tick
   learned.json      the biosphere GENOME (adopted operants)

7. ORGAN ROLES
------------------------------------------------------------------------
   i4          identity root  : seeds the biosphere (L1 self-reference)
   agent       learner+consensus : attests frozen spec, PROPOSES an operant
   subagent    L2 hosted learner : hosted on 18-bit SUBAGENT HOST plane
   cortex      L4 governor+sensor : ARBITRATES, RESOLVES deep operand, SENSES
   constructor L3 assembler : builds + VERIFIES the Merkle collapse
   jitonf      runtime : EXECUTES the woven I-13 program (gated by verdict)
   f1..f4      folds : the factory/language/machine collapses (sealed artifacts)

8. HOW IT IS WIRED (tight structure first)
------------------------------------------------------------------------
   bios/kernel.py  boots from i4, adds slaughterhouse5/ to sys.path,
                   registers organs lazily, holds shared state + tick.
   bios/contract.py  the Capsule — the only message organs exchange.
   bios/state.py    file-based persistent memory (transparent, git-versioned).
   bios/pulse.py    the loop driver — the descent + governance + evolution.
   All behavior is wired incrementally and is ALWAYS genuine
   (real fold verify, real consensus, real IVM execution) — never simulated.

========================================================================

========================================================================
| 9. FEATURE STATUS — everything on the roadmap is now built                 |
========================================================================

  [BUILT] tight structure first (one planet, one repo, ten module organs)
  [BUILT] kernel + Capsule contract + file-based persistent state
  [BUILT] wire EXECUTE + FOLD to real organs (jitonf runs, constructor verifies)
  [BUILT] multi-plane governance: L1 agents + L2 subagents independently propose
  [BUILT] cortex ARBITRATES the combined population at 2/3; logs EVERY difference
  [BUILT] COMPOSE weaves an adopted operant's REAL semantics into the program
  [BUILT] population PERSISTS + EVOLVES (fitness / gen / selection)
  [BUILT] TEACH signal feeds differences back; minorities are taught to agree
  [BUILT] taught LESSON persisted in the genome (remembered across runs)
  [BUILT] L4 deep-operand RESOLVER selects what executes (a wall)
  [BUILT] L4 trained weight folds into the run + genome reinforcement
  [BUILT] L4 weight MODULATES the teach strength
  [BUILT] FUSE: ALL adopted operants woven into ONE program at once
  [BUILT] REAL operant forms in jitonf (jitonf.operants.lower)
  [BUILT] agents INGEST prior capsules (self-reference of own output)
  [BUILT] RESUME: state persists across runs (python -m bios.pulse --continue)
  [BUILT] L4 weight is a LEARNED parameter (state/learned_weight.json)
  [BUILT] SPECIATION: separate instances cross-pollinate genomes (bios.speciate)
  [BUILT] LIVE PULSE viewer generated each run (pulse-view.html)

  Run:  python -m bios.pulse --reset      (fresh) | --continue (resume)
  Speciate:  python -m bios.speciate 5
========================================================================
