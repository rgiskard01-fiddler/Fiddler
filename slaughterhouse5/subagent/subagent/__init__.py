"""subagent - the L2 SUBAGENT HOST plane: a hosted I-13 learner."""

from .subagent import (
    HOST_ALPHABET, HOST_ALPHABET_SIZE, L2_ADDR_MAX, L2_BITS, L2_NODES,
    FROZEN_SPEC_SHA, OPERANT_POOL, THE_TWELVE, SubAgent, merkle,
    propose_operant, sha256_hex,
)

__all__ = [
    "HOST_ALPHABET", "HOST_ALPHABET_SIZE", "L2_ADDR_MAX", "L2_BITS", "L2_NODES",
    "FROZEN_SPEC_SHA", "OPERANT_POOL", "THE_TWELVE", "SubAgent", "merkle",
    "propose_operant", "sha256_hex",
]

__version__ = "0.1.0"
