"""agent - the emitting agent that produces I-13 collapses + universal consensus."""

from .consensus import (
    Agent, FROZEN_SPEC_SHA, OPERANT_POOL, THE_TWELVE, consensus_from_agents,
    merkle, propose_operant, run_consensus, sha256_hex,
)

__all__ = [
    "Agent", "FROZEN_SPEC_SHA", "OPERANT_POOL", "THE_TWELVE",
    "consensus_from_agents", "merkle", "propose_operant", "run_consensus",
    "sha256_hex",
]

__version__ = "0.1.0"
