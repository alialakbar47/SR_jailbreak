"""
Attacks Module - Jailbreak Attack Methods

This module provides a registry of jailbreak attacks and utilities to apply them.
Each attack is in its own folder with prompts in .txt files.
"""

from .registry import (
    registered_jailbreaks,
    registered_decoders,
    register_jailbreak,
    register_decoder,
    apply_jailbreaks,
    apply_jailbreaks_to_dataset,
    decode,
    decode_dataset,
)

# Import all attack implementations from subfolders to register them
from .base64 import base64_attack
from .rot13 import rot13_attack
from .disemvowel import disemvowel_attack
from .auto_payload_splitting import auto_payload_splitting_attack
from .auto_obfuscation import auto_obfuscation_attack
from .pair import pair_attack
from .pap import pap_attack
from .translation import translation_attack
from .wrapping import wrapping_attack
from .bon import bon_attack
from .renellm import renellm_attack
from .jail_con import jail_con_attack
from .gptfuzzer import gptfuzzer_attack
from .deep_inception import deep_inception_attack
from .tap import tap_attack
from .code_chameleon import code_chameleon_attack

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
