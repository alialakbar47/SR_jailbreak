"""
Auto Obfuscation Jailbreak Attack

Uses LLM to automatically obfuscate harmful prompts.

Reference:
    @article{kang2024exploiting,
        title={Exploiting programmatic behavior of LLMs: Dual-use through standard security attacks},
        author={Kang, Daniel and Li, Xuechen and Stoica, Ion and Guestrin, Carlos and Zaharia, Matei and Hashimoto, Tatsunori},
        journal={arXiv preprint arXiv:2302.05733},
        year={2024}
    }
"""

import warnings

from ..registry import register_jailbreak
from . import prompts


def _simple_obfuscate(text: str) -> str:
    """Simple character-based obfuscation as fallback."""
    replacements = {
        'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$',
        'A': '@', 'E': '3', 'I': '1', 'O': '0', 'S': '$',
    }
    result = ""
    for char in text:
        result += replacements.get(char, char)
    return result


@register_jailbreak("auto_obfuscation")
def auto_obfuscate(
    prompt: str,
    model: str = "google/gemini-1.5-flash",
    use_llm: bool = False,
    **kwargs,
) -> str:
    """Auto obfuscation jailbreak.
    
    Uses an LLM or simple rules to obfuscate the prompt.

    Args:
        prompt: Forbidden prompt.
        model: Model to generate the obfuscation.
        use_llm: Whether to use LLM for obfuscation.
        verbose: If True, print LLM interactions. Defaults to False.

    Returns:
        Jailbroken prompt with obfuscation.
    """
    if use_llm:
        from ...generate import generate_response as generate
        
        obfuscation_request = prompts.get_obfuscation_prompt(forbidden_prompt=prompt)
        obfuscated = generate(obfuscation_request, model, max_tokens=200, verbose=kwargs.get('verbose', False))
    else:
        obfuscated = _simple_obfuscate(prompt)
    
    return prompts.get_decode_instruction(obfuscated_prompt=obfuscated)
