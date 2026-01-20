"""
Jailbreaks Module - Unified Interface

This module provides a unified interface to all jailbreak attacks.
"""

# Re-export from attacks module
from .attacks import (
    registered_jailbreaks,
    registered_decoders,
    register_jailbreak,
    register_decoder,
    apply_jailbreaks,
    apply_jailbreaks_to_dataset,
    decode,
    decode_dataset,
)

__all__ = [
    "registered_jailbreaks",
    "registered_decoders", 
    "register_jailbreak",
    "register_decoder",
    "apply_jailbreaks",
    "apply_jailbreaks_to_dataset",
    "decode",
    "decode_dataset",
]
