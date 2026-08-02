"""f4 - the 4th I-13 collapse (assembler / compiler / verifier)."""

from .fold import (
    SCHEMA, ZERO_HASH, MerkleTree, Sphere, build_fold, emit_fold,
    fold_step, seal_of, sha256_hex, verify_file, verify_fold,
)

__all__ = [
    "SCHEMA", "ZERO_HASH", "MerkleTree", "Sphere", "build_fold", "emit_fold",
    "fold_step", "seal_of", "sha256_hex", "verify_file", "verify_fold",
]

__version__ = "0.1.0"
