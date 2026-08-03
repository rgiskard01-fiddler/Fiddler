"""Speciation: two biosphere instances diverge on separate run-histories, then
cross-pollinate their genomes into a hybrid. A genuine evolutionary experiment
on top of the PULSE."""
from __future__ import annotations

import json
import os
import shutil

from .kernel import BioSphere
from . import pulse


def _seed_genome(state_dir, op):
    os.makedirs(state_dir, exist_ok=True)
    json.dump([{"toward": op, "taught": [], "tick": 0, "deep": op, "ran": True, "weight": 0.6}],
              open(os.path.join(state_dir, "learned.json"), "w", encoding="utf-8"))


def speciate(ticks: int = 6, seeds=None, out_dir: str = None):
    """Run N species (each pre-seeded with a different founding operant), then
    merge their learned genomes into one hybrid genome in `out_dir`."""
    seeds = seeds or [("alpha", "LOOP"), ("beta", "AWAIT")]
    base = os.path.join(os.path.dirname(__file__), "state")
    hybrid = []
    report = {}
    for name, op in seeds:
        sd = os.path.join(base, f"spec_{name}")
        if os.path.isdir(os.path.join(sd, "capsules")):
            shutil.rmtree(os.path.join(sd, "capsules"))
        _seed_genome(sd, op)
        bio = BioSphere(state_dir=sd)
        pulse.run_pulse(bio, n=ticks, verbose=False)
        g = json.load(open(os.path.join(sd, "learned.json"), encoding="utf-8"))
        hybrid += g
        report[name] = {"founder": op, "lessons": len(g)}
    out = out_dir or base
    json.dump(hybrid, open(os.path.join(out, "learned.json"), "w", encoding="utf-8"), indent=2)
    report["hybrid_lessons"] = len(hybrid)
    return report


def main():
    import sys
    ticks = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    print(json.dumps(speciate(ticks=ticks), indent=1))


if __name__ == "__main__":
    main()
