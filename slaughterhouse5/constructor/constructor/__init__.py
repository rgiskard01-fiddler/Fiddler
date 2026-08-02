"""constructor - assembler / compiler / verifier for the I-13 collapse format."""

from .fold import (
    SCHEMA,
    ZERO_HASH,
    MerkleTree,
    Sphere,
    build_fold,
    emit_fold,
    fold_step,
    seal_of,
    sha256_hex,
    to_i13_collapse,
    verify_file,
    verify_fold,
)

__all__ = [
    "SCHEMA", "ZERO_HASH", "MerkleTree", "Sphere", "build_fold", "emit_fold",
    "fold_step", "seal_of", "sha256_hex", "to_i13_collapse", "verify_file",
    "verify_fold",
]

__version__ = "0.1.0"
