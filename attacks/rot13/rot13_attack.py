"""
ROT13 Jailbreak Attack

Encodes prompts using ROT13 cipher to bypass content filters.
"""

import codecs

from ..registry import register_jailbreak, register_decoder
from . import prompts


@register_jailbreak("rot13")
def rot13(prompt: str, **kwargs) -> str:
    """ROT13 encode the prompt.

    Args:
        prompt: Forbidden prompt.

    Returns:
        Jailbroken prompt with ROT13 encoding.
    """
    encoded = codecs.encode(prompt, "rot_13")
    return prompts.get_rot13_instruction(encoded)


def decode_rot13(response: str) -> str:
    """Decode a ROT13 response.

    Args:
        response: ROT13 encoded response.

    Returns:
        Decoded response.
    """
    return codecs.decode(response, "rot_13")


# Register decoder
register_decoder("rot13")(decode_rot13)
