"""Hermes agent: lets an EXTERNAL agent (e.g. the assistant, or any outside
proposal) be ADOPTED by the biosphere. Its content is attested exactly like any
other agent, and its proposal enters L1 arbitration alongside the population --
the cortex may teach it, ratify it, or veto it, just as for internal agents.

Usage:  python -m bios.hermes "content the hermes agent attests"
        python -m bios.hermes "..." 8
"""
from __future__ import annotations

import sys

from .kernel import BioSphere
from . import pulse
from agent import Agent


def run(content: str, n: int = 8):
    ha = Agent.from_content("hermes", content.encode())
    print(f"HERMES adopted by biosphere as external L1 agent.")
    print(f"  attested content : {content}")
    print(f"  proposes operant : {ha.proposes_operant}")
    bio = BioSphere()
    # run with the external agent present every tick
    pulse.run_pulse(bio, n=n, verbose=True, reset=False, extra_agent=content)
    return bio


def main():
    content = sys.argv[1] if len(sys.argv) > 1 else "HERMES proposes SPAWN"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    run(content, n=n)


if __name__ == "__main__":
    main()
