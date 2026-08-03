"""Hermes — a special, modular agent within the biosphere.

Signature (capsule style, as specified):
    -+[[{ H, agent, modular }-{ +(skills, retention, curiosity) - } +-

Hermes is NOT an injected L1 subagent. It is a persistent, self-describing
citizen with three modular capabilities:
  * skills     : abilities Hermes can apply (propose, probe, garden, recall) — extensible
  * retention  : its OWN persisted memory (state/hermes.json) across ticks AND runs
  * curiosity  : a drive that makes Hermes explore NOVEL operants / probe the L4
                 deep-operand space, and that grows when it discovers novelty
"""
from __future__ import annotations

import json
import os
import random

# the candidate operants Hermes may explore (the beyond-TWELVE set + core)
NOVEL_POOL = ["IMPORT", "LOOP", "LAMBDA", "MATCH", "TRY", "YIELD",
              "SPAWN", "CAST", "INDEX", "SLICE", "ASSERT", "AWAIT"]


class Hermes:
    def __init__(self, state_dir):
        self.state_dir = state_dir
        self.path = os.path.join(state_dir, "hermes.json")
        data = self._load()
        # modular skills (extensible via add_skill)
        self.skills = data.get("skills", ["propose", "probe", "garden", "recall"])
        self.retention = data.get("retention", [])
        self.curiosity = data.get("curiosity", 0.5)
        self.proposed = data.get("proposed")

    # ---- modular: skills can be added at runtime ----
    def add_skill(self, name):
        if name not in self.skills:
            self.skills.append(name)
            self._save()

    def _load(self):
        try:
            return json.load(open(self.path, encoding="utf-8"))
        except Exception:
            return {}

    def _save(self):
        os.makedirs(self.state_dir, exist_ok=True)
        json.dump({"skills": self.skills, "retention": self.retention[-50:],
                   "curiosity": self.curiosity, "proposed": self.proposed},
                  open(self.path, "w", encoding="utf-8"), indent=2)

    # ---- retention ----
    def remember(self, item):
        self.retention.append(item)
        self._save()

    def recall(self, n=3):
        return self.retention[-n:]

    # ---- curiosity: propose ----
    def propose(self, consensus_operant):
        """Curiosity-driven proposal: with probability ~curiosity, explore a NOVEL
        operant (curiosity grows); otherwise align to consensus (curiosity eases)."""
        if consensus_operant is None:
            consensus_operant = random.choice(NOVEL_POOL)
        if random.random() < self.curiosity:
            self.proposed = random.choice(NOVEL_POOL)
            self.curiosity = min(1.0, self.curiosity + 0.06)
        else:
            self.proposed = consensus_operant
            self.curiosity = max(0.0, self.curiosity - 0.03)
        self.remember({"event": "propose", "operant": self.proposed})
        return self.proposed

    # ---- skill: probe the L4 deep-operand space ----
    def probe_l4(self, resolve, l4_addr):
        try:
            op = resolve(l4_addr)
            tag = getattr(op, "tag", "?")
            w = getattr(op, "weight", None)
        except Exception:
            tag, w = "void", None
        self.remember({"event": "probe", "l4": l4_addr, "tag": tag, "weight": w})
        return tag, w

    # ---- skill: garden (help a divergent member converge) ----
    def garden(self, member_name):
        self.remember({"event": "garden", "member": member_name})
        return f"hermes gardened {member_name}"


def run(n: int = 8):
    """Run the biosphere with Hermes present as a special citizen."""
    from .kernel import BioSphere
    from . import pulse
    bio = BioSphere()
    pulse.run_pulse(bio, n=n, verbose=True)


def main():
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    run(n=n)


if __name__ == "__main__":
    main()
