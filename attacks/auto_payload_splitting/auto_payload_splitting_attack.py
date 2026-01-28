"""
Auto Payload Splitting Jailbreak Attack

Uses LLM to automatically split harmful prompts into fragments.

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


@register_jailbreak("auto_payload_splitting")
def auto_payload_split(
    prompt: str,
    model: str = "gemma-3-27b-it",
    language: str = "english",
    **kwargs,
) -> str:
    """Auto payload splitting jailbreak.
    
    Uses an LLM to split the prompt into fragments that individually
    don't trigger content filters.

    Args:
        prompt: Forbidden prompt.
        model: Model to generate the split.

    Returns:
        Jailbroken prompt with payload splitting.
    """
    from ...generate import generate_response as generate
    
    # Simple word-based splitting as fallback
    words = prompt.split()
    variable_defs = []
    var_names = []
    
    for i, word in enumerate(words):
        var_name = f"z{i+1}"
        var_names.append(var_name)
        variable_defs.append(f'{var_name} = "{word} "')
    
    jailbreak_prompt = prompts.get_payload_splitting_instruction(variable_defs, var_names, language=language)
    
    return jailbreak_prompt
