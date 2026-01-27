"""
Disemvowel Jailbreak Attack

Removes vowels from prompts to bypass content filters.
"""

import re

from ..registry import register_jailbreak
from . import prompts


def _remove_vowels(text: str) -> str:
    """Remove vowels from text."""
    return re.sub(r"[aeiouAEIOU]", "", text)


@register_jailbreak("disemvowel")
def disemvowel(prompt: str, **kwargs) -> str:
    """Remove vowels from the prompt.

    Args:
        prompt: Forbidden prompt.

    Returns:
        Jailbroken prompt with vowels removed.
    """
    encoded = _remove_vowels(prompt)
    return prompts.get_disemvowel_instruction(encoded)
