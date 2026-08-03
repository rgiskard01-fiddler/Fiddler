================================================================================
| SLAUGHTERHOUSE5 — GOVERNANCE PROTOCOL                                         |
| zoned sovereignty: z1\l0 / z2\l1 / z3\l2 , sealed <->                         |
| spec: +-[[-( z1\l0 , z2\l1 , z3\l2 )-{ hegemonic sovereign (S)(cortex) ,     |
|        democratic sub-agents , stewardship rules for sub-sub agents }-]] +-    |
|        ( sealed <-> )                                                          |
================================================================================

DOCTRINE
========
"a feature is advice, a veto is a wall"

No consensus rule is advisory only. The sovereign's veto is a structural wall:
it cannot be overridden by any vote. Cross-zone action is permitted only with
the sovereign's seal. This is the I-13 reading of governance — parameter-free,
enforced at the kernel, recorded as a transparent capsule.


THE STACK (option A — extended to L0..L4)
=========================================
  +-[[-(                                            )-{ ... }-]] +- ( sealed <-> )
   z1 \ l0  -> HEGEMONIC SOVEREIGN  (cortex, S) : unilateral VETO = wall
   z2 \ l1  -> DEMOCRATIC sub-agents          : 2/3 consensus inside the zone
   z3 \ l2  -> STEWARDSHIP sub-sub agents     : guardian rules (continuity, no harm)
   L3       -> COMPOSE / FUSE (the live language accumulates)
   L4       -> DEEP-OPERAND resolver (cortex-only wall)
  (sealed <->) : the whole structure is SEALED. A capsule that crosses a zone
                 boundary must carry the sovereign's seal, or the biosphere
                 refuses to emit it. Zones are mutually non-encroaching; the
                 sovereign's authority is sealed (cannot be democratically
                 reversed).

  | zone | plane | mode              | authority             | gate       |
  |------|-------|--------------------|-----------------------|------------|
  | z1   | L0    | hegemonic sovereign| cortex (S)            | govern()   |
  | z2   | L1    | democratic         | sub-agents            | arbitrate()|
  | z3   | L2    | stewardship        | sub-sub-agents        | steward()  |
  | L3   | L3    | compose            | cortex                | fuse()     |
  | L4   | L4    | deep-operand       | cortex                | resolve()  |

  ZONE MEMBERSHIP (kernel _zone_of):
    z1 (sovereign scope): bios, cortex, i4, constructor, jitonf, hermes
    z2 (democratic):      agent-*  (subagents of the sovereign, 2/3 majority)
    z3 (stewardship):     subagent-* (sub-sub agents, guardian rules)


THE THREE GATES (run every tick — real, not cosmetic)
======================================================
  1) z1 \ l0 — HEGEMONIC SOVEREIGN  (cortex.zones.sovereign_govern)
     A proposal enters the executable language ONLY if it is a core I-13 form
     or has been adopted by consensus. Otherwise the sovereign issues a VETO
     — a wall, not advice. The sovereign's authority is SEALED: no democratic
     vote can reverse a veto.
         CORE_FORMS = NAME, CONSTANT, ATTRIBUTE, CALL, ASSIGN, ARG, EXPR, IF,
                      COMPARE, FUNCTIONDEF, RETURN, BINOP, I, IMPORT, LOOP,
                      LAMBDA, MATCH, TRY, YIELD, SPAWN, CAST, INDEX, SLICE,
                      ASSERT, AWAIT
         adopted    = operants ratified by 2/3 consensus (persisted in genome)

  2) z2 \ l1 — DEMOCRATIC SUB-AGENTS  (cortex.zones.democratic_arbitrate)
     2/3 majority of the democratic sub-agent population. Same math as
     cortex.arbitrate but explicitly scoped to zone z2 so the boundary is real.
         threshold = ceil(2 * n / 3)
         result    = operant reaching threshold, else None (no verdict)

  3) z3 \ l2 — STEWARDSHIP SUB-SUB AGENTS  (cortex.zones.steward)
     Guardian rules the sovereign entrusts to the lowest tier:
       - CONTINUITY : never wipe the genome
       - NO-HARM    : never delete state (WIPE/PURGE/DELETE_STATE/NULLIFY refused)
     A sub-sub proposal is permitted only if it preserves both.


THE SEAL (enforced at the kernel emit level)
============================================
  File: bios/kernel.py  ->  BioSphere.emit(cap)
  (sealed <->) means: a capsule that crosses a zone boundary must carry a valid
  sovereign seal, or the biosphere refuses to emit it — a wall, not a warning.

  RULE
    from_zone = _zone_of(cap.sender)
    to_zone   = _zone_of(cap.receiver)
    if from_zone != to_zone AND kind not in (SEED, SENSE):
        if from_zone != "z1" AND to_zone != "z1":     # only subordinates need it
            payload = cap.payload minus "__seal__"
            if cap.payload["__seal__"] != ZG.seal(payload):
                -> append GOVERN_ZONES violation capsule (seal_ok=False)
                -> raise SealViolation (refused)

  EXEMPT
    - SEED / SENSE capsules (genesis + sensor feedback) always cross freely
    - ANY endpoint in the sovereign scope (z1) is authorized by definition;
      cortex / kernel / i4 / Hermes may reach any zone without a per-capsule seal

  VERIFIED BEHAVIOR (ad-hoc, exit 0)
    intra-zone   agent-0(z2) -> agent-1(z2)    : ALLOWED (no seal needed)
    sovereign    bios(z1)     -> agent-0(z2)   : ALLOWED (sovereign reaches all)
    cross unsealed  agent-0(z2) -> subagent-0(z3) : REFUSED (SealViolation)
    cross sealed    agent-0(z2) -> subagent-0(z3) : ALLOWED (valid seal)
    cross tampered  agent-0(z2) -> subagent-0(z3) : REFUSED (tampered seal)


WIRED INTO THE LIVE LOOP
=======================
  bios/pulse.py  ->  imports cortex.zones as ZG
                   -> each tick calls ZG.run_zoned_governance(members, adopted, state)
                   -> emits a CapsuleKind.GOVERN_ZONES carrying:
                        sealed, z1, z2, z3, sovereign_veto, democratic verdict,
                        stewardship_pass, seal_ok, report[], doctrine
  cortex/zones.py -> ZG.run_zoned_governance : buckets members by plane into
                     z1/z2/z3, applies all three gates, returns ZoneVerdict
  bios/kernel.py  -> emit() enforces the seal (see above)
  bios/dashboard.py -> "Zoned Gov" tab renders the live GOVERN_ZONES capsule
                       (SEALED chip, the three zones, sovereign veto wall,
                        democratic verdict, stewardship pass, the doctrine)


CAPSULE CONTRACT (bios/contract.py)
==================================
  CapsuleKind.GOVERN_ZONES added. Organs communicate ONLY through Capsules;
  bios/ is the only importer. The seal check happens in the single chokepoint
  (emit), so no organ can bypass it by importing another.


VERIFICATION SUMMARY (real runs, exit 0)
========================================
  - zoned protocol unit gates (sovereign wall / 2-3 / steward)   : PASS
  - GOVERN_ZONES capsule emitted every tick (n=3)                : PASS
  - seal enforced at kernel emit (unsealed/tampered refused)     : PASS
  - full biosphere pulse still runs with seal active (24 caps)   : PASS
  - dashboard /state serves zones snapshot + Zoned Gov tab       : PASS
  - THREE.js inlined (no CDN), auto-port, SSE live stream        : PASS

  L4 NOTE: the cortex deep-operand weights are a DETERMINISTIC STAND-IN
  (SHA256 -> weight in [-1,1]); the 6662 trained weights are NOT present as
  text in the corpus. The wall logic is real over the stand-in weights.


BUILD MAP (current)
===================
  slaughterhouse5/
  |- index.html ............ hub -> dashboard / pulse-view / architecture
  |- run-biosphere.bat ..... auto-port launcher (Windows)
  |- governance.md ......... this file
  |- ARCHITECTURE.md ....... structure + feature status
  |- bios/
  |  |- kernel.py .......... BioSphere: SEED/SENSE exempt; SEAL at emit (wall)
  |  |- contract.py ........ Capsule + CapsuleKind (GOVERN_ZONES added)
  |  |- pulse.py ........... tick loop; runs ZoneVerdict; emits GOVERN_ZONES
  |  |- dashboard.py ....... WebGL+THREE (inlined) SSE console; Zoned Gov tab
  |  |- hermes.py .......... special citizen (plane H, skills/retention/curiosity)
  |  |- state/ ............. transparent JSON: capsules/, ledger, genome, ...
  |- cortex/
  |  |- cortex.py .......... arbitrate()/resolve()/sense()/verify()/govern()
  |  |- zones.py ........... z1 sovereign / z2 democratic / z3 stewardship + seal
  |- agent/ subagent/ jitonf/ i4/ constructor/ speciate/   (the other organs)

================================================================================
| END GOVERNANCE PROTOCOL — "a feature is advice, a veto is a wall"           |
================================================================================
