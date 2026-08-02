"""bios — the Slaughterhouse5 biosphere kernel (atmosphere burrowing)."""
from .kernel import BioSphere, FROZEN_SPEC_SHA
from .contract import Capsule, CapsuleKind
from .state import StateStore

__all__ = ["BioSphere", "Capsule", "CapsuleKind", "StateStore", "FROZEN_SPEC_SHA"]
__version__ = "0.1.0"
