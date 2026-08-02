"""cortex - the L4 DEEP OPERAND plane: governor + sensor of the I-13 stack."""

from .cortex import (
    L4_ADDR_MAX, L4_BITS, L4_NODES, PLANES, PLANE_ORDER, RULE_REACH,
    SENSE_L1, SENSE_L2, Cortex, CortexBoundary, Operand, build_operand_table,
    VETO_MSG,
)

__all__ = [
    "L4_ADDR_MAX", "L4_BITS", "L4_NODES", "PLANES", "PLANE_ORDER",
    "RULE_REACH", "SENSE_L1", "SENSE_L2", "Cortex", "CortexBoundary",
    "Operand", "build_operand_table", "VETO_MSG",
]

__version__ = "0.1.0"
