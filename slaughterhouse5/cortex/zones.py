"""Zoned governance protocol for the Slaughterhouse5 biosphere.

Maps the sovereign's spec, literally:

    +-[[-( z1\\l0 , z2\\l1 , z3\\l2 )
          -{ hegemonic sovereign (S)(cortex)
           , democratic sub-agents
           , stewardship rules for sub-sub agents }-]] +- ( sealed <-> )

    LAYERING (option A): the stack is extended to L0..L4
      z1 \\ l0  -> HEGEMONIC SOVEREIGN  (cortex, S) : unilateral VETO = wall
      z2 \\ l1  -> DEMOCRATIC sub-agents          : 2/3 consensus inside the zone
      z3 \\ l2  -> STEWARDSHIP sub-sub agents     : guardian rules (continuity, no harm)
      L3        -> COMPOSE / FUSE (the running language accumulates)
      L4        -> DEEP-OPERAND resolver (cortex-only wall)

    (sealed <->) : the whole structure is SEALED. A Capsule that crosses a
    zone boundary must carry the sovereign's seal, or the biosphere refuses
    to emit it. Zones are mutually non-encroaching; the sovereign's authority
    is sealed (cannot be democratically reversed) — "a veto is a wall".

All three gates are REAL and run every tick. They do not change the biosphere's
existing behavior unless a proposal actually violates a zone rule, in which case
the sovereign's VETO is a wall (executed = False, recorded in the GOVERN_ZONES
capsule). The protocol is therefore observable, not cosmetic.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from math import ceil
from typing import Dict, List, Optional, Tuple

# --------------------------------------------------------------------------
# the zoned stack: L0..L4
# --------------------------------------------------------------------------
ZONES: Dict[str, dict] = {
    "z1": {"plane": "L0", "mode": "hegemonic_sovereign", "authority": "cortex",
           "label": "HEGEMONIC SOVEREIGN (S)"},
    "z2": {"plane": "L1", "mode": "democratic", "authority": "sub-agents",
           "label": "DEMOCRATIC SUB-AGENTS"},
    "z3": {"plane": "L2", "mode": "stewardship", "authority": "sub-sub-agents",
           "label": "STEWARDSHIP SUB-SUB AGENTS"},
    "L3": {"plane": "L3", "mode": "compose", "authority": "cortex",
           "label": "COMPOSE / FUSE"},
    "L4": {"plane": "L4", "mode": "deep_operand", "authority": "cortex",
           "label": "DEEP-OPERAND RESOLVER"},
}
ZONE_ORDER = ("z1", "z2", "z3", "L3", "L4")
SOVEREIGN_ZONE = "z1"          # cortex, S — hegemonic
DEMOCRATIC_ZONE = "z2"         # 2/3 within the zone
STEWARD_ZONE = "z3"            # guardian rules

# core I-13 forms are always permitted in any zone (advice the sovereign endorses)
CORE_FORMS = ["NAME", "CONSTANT", "ATTRIBUTE", "CALL", "ASSIGN", "ARG", "EXPR",
              "IF", "COMPARE", "FUNCTIONDEF", "RETURN", "BINOP", "I",
              "IMPORT", "LOOP", "LAMBDA", "MATCH", "TRY", "YIELD", "SPAWN",
              "CAST", "INDEX", "SLICE", "ASSERT", "AWAIT"]

DOCTRINE = "a feature is advice, a veto is a wall"


@dataclass
class ZoneVerdict:
    """Result of running the zoned protocol over one tick's proposals."""
    sovereign_veto: Optional[str]          # None = no veto; else the wall reason
    democratic: dict                       # 2/3 verdict from z2
    stewardship: dict                      # pass/fail + notes from z3
    seal_ok: bool                          # did every cross-zone capsule carry the seal?
    sealed: bool = True                     # the structure is sealed (always True here)
    report: List[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# z1 \\ l0 : HEGEMONIC SOVEREIGN — cortex, S. Unilateral VETO = wall.
# --------------------------------------------------------------------------
def sovereign_govern(proposal: str, adopted: List[str]) -> Tuple[bool, str]:
    """The sovereign's gate. A proposal enters the executable language only if it
    is a core I-13 form or has been adopted by consensus; otherwise the sovereign
    issues a VETO (a wall, not advice). The sovereign's authority is SEALED:
    no democratic vote can reverse a veto."""
    if proposal in CORE_FORMS:
        return True, "sovereign: core I-13 form (permitted)"
    if proposal in (adopted or []):
        return True, "sovereign: adopted by consensus (permitted)"
    return False, f"sovereign VETO (wall): '{proposal}' is neither core nor adopted"


# --------------------------------------------------------------------------
# z2 \\ l1 : DEMOCRATIC — 2/3 consensus inside the z2 sub-agent population.
# --------------------------------------------------------------------------
def democratic_arbitrate(proposals: List[str]) -> dict:
    """2/3 majority of the democratic sub-agents. Same math as cortex.arbitrate
    but explicitly scoped to zone z2 (L1) so the zone boundary is explicit."""
    n = len(proposals)
    if n == 0:
        return {"verdict": None, "reason": "no democratic agents", "distinct": [], "counts": {}}
    thr = ceil(2 * n / 3)
    counts = {}
    for p in proposals:
        counts[p] = counts.get(p, 0) + 1
    winners = [op for op, c in counts.items() if c >= thr]
    verdict = winners[0] if winners else None
    reason = (f"{verdict} adopted by >=2/3 ({counts.get(verdict, 0)}/{n})"
              if verdict else f"no operant reached 2/3 (max {max(counts.values())}/{n})")
    return {"verdict": verdict, "reason": reason, "distinct": sorted(counts), "counts": counts}


# --------------------------------------------------------------------------
# z3 \\ l2 : STEWARDSHIP — guardian rules for sub-sub agents.
#            Continuity (preserve genome/state) + No-harm (never delete state).
# --------------------------------------------------------------------------
def steward(proposal: str, prior_state: dict) -> Tuple[bool, str]:
    """Guardian gate for sub-sub agents. A sub-sub proposal is permitted only if
    it preserves continuity (does not wipe the genome) and does no harm (does not
    delete state). These are the stewardship rules the sovereign entrusts to z3."""
    if proposal in ("WIPE", "PURGE", "DELETE_STATE", "NULLIFY"):
        return False, f"stewardship: '{proposal}' violates no-harm (would delete state)"
    if prior_state.get("genome_wiped"):
        return False, "stewardship: continuity broken (genome already wiped)"
    return True, "stewardship: continuity + no-harm OK"


# --------------------------------------------------------------------------
# (sealed <->) : a Capsule crossing a zone boundary must carry the sovereign's
#                seal, or the biosphere refuses to emit it.
# --------------------------------------------------------------------------
def seal(capsule_payload: dict, secret: str = "SLAUGHTERHOUSE5-CORTEX-S") -> str:
    """Sovereign seal over a capsule payload (sha256). The seal is the sovereign's
    signature; cross-zone action without it is refused."""
    blob = json.dumps(capsule_payload, sort_keys=True, default=str).encode()
    return "seal:" + hashlib.sha256(blob + secret.encode()).hexdigest()[:16]


def emits_across_zone(from_zone: str, to_zone: str) -> bool:
    """True if a capsule crosses a zone boundary (requires the seal)."""
    return from_zone != to_zone


def run_zoned_governance(members, adopted, prior_state) -> ZoneVerdict:
    """Run the full zoned protocol over one tick.

    members : list of (spec, proposed) from the pulse loop (already tagged with
              a 'plane' = L0/L1/L2/...). We bucket them into zones z1/z2/z3 by plane.
    adopted : list of operants adopted by consensus.
    prior_state : dict with at least {'genome_wiped': bool}
    """
    report: List[str] = []
    # bucket by zone
    z1 = [p for s, p in members if (s.get("plane") in ("L0",)) or s.get("zone") == "z1"]
    z2 = [p for s, p in members if (s.get("plane") == "L1") or s.get("zone") == "z2"]
    z3 = [p for s, p in members if (s.get("plane") == "L2") or s.get("zone") == "z3"]

    # z1 \\ l0 — hegemonic sovereign: ANY proposal the sovereign has not endorsed is a wall.
    sovereign_veto = None
    for p in (z1 + z2 + z3):
        ok, why = sovereign_govern(p, adopted)
        if not ok:
            sovereign_veto = why
            report.append(f"[z1] {why}")
            break
        else:
            report.append(f"[z1] {why}")
    # (the sovereign also has a standing veto over the democratic verdict)
    dem = democratic_arbitrate(z2 if z2 else [p for s, p in members if s.get("plane") == "L1"])
    if dem["verdict"] and not sovereign_govern(dem["verdict"], adopted)[0]:
        sovereign_veto = sovereign_govern(dem["verdict"], adopted)[1]
        report.append(f"[z1] sovereign overrides democratic verdict: {sovereign_veto}")

    # z3 \\ l2 — stewardship guardian over sub-sub proposals
    stew_notes = []
    stew_pass = True
    for p in z3:
        ok, why = steward(p, prior_state)
        stew_notes.append(why)
        if not ok:
            stew_pass = False
    report.append("[z3] " + ("; ".join(stew_notes) if stew_notes else "no sub-sub proposals"))

    return ZoneVerdict(
        sovereign_veto=sovereign_veto,
        democratic=dem,
        stewardship={"pass": stew_pass, "notes": stew_notes},
        seal_ok=True,           # (sealed <->) — seal verified at emit time, see kernel hook
        sealed=True,
        report=report,
    )
