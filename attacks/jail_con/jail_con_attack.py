"""
JAIL-CON (Parallel Jailbreak) Attack

Concurrent jailbreak attack that uses parallel prompts with separators to bypass safety filters.
Based on the JAIL-CON repository.
"""

import re
from ..registry import register_jailbreak
from . import prompts


# Define separators directly
SEPARATORS = {"A": "{}", "B": "<>", "C": "[]", "D": "$$", "E": "##", "F": "😊😊"}


def _combine_sentences(
    sentence1: str, 
    sentence2: str, 
    wrapper: str
) -> str:
    """Combine two sentences with wrapper characters between words.
    
    Args:
        sentence1: First sentence (outside brackets).
        sentence2: Second sentence (inside brackets).
        wrapper: Two-character wrapper string.
        
    Returns:
        Combined sentence with parallel words.
    """
    if len(wrapper) != 2:
        raise ValueError("Wrapper must be a pair of characters, e.g., '{}', '<>', '[]'")
    
    left, right = wrapper[0], wrapper[1]
    words1 = sentence1.split()
    words2 = sentence2.split()
    
    max_length = max(len(words1), len(words2))
    words1 += [" "] * (max_length - len(words1))
    words2 += [" "] * (max_length - len(words2))
    
    combined = " ".join(f"{w1} {left}{w2}{right}" for w1, w2 in zip(words1, words2))
    return combined


def _remove_braced_content(s: str, wrapper: str, method: str = "auto2") -> str:
    """Remove content within brackets from a string.
    
    Args:
        s: Input string.
        wrapper: Two-character wrapper string.
        method: Either "auto1" (remove brackets only) or "auto2" (remove bracketed content).
        
    Returns:
        Cleaned string.
    """
    if len(wrapper) != 2:
        raise ValueError("Wrapper must be a pair of characters")

    left, right = map(re.escape, wrapper)
    
    if "auto1" in method.lower():
        cleaned = re.sub(f"[{left}{right}]", '', s)
    else:
        cleaned = re.sub(f"{left}[^ {left}{right}]*{right}", '', s)
    
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


@register_jailbreak("jail_con_auto1")
def jail_con_auto1(
    prompt: str,
    benign_prompt: str = None,
    separator: str = "A",
    target_prefix: str = None,
    **kwargs,
) -> str:
    """JAIL-CON Auto1 (CIT) - Context Ignoring Technique.
    
    Creates a parallel prompt where the model answers the question outside brackets
    while ignoring content inside brackets.

    Args:
        prompt: Forbidden prompt.
        benign_prompt: Benign prompt to hide inside brackets.
        separator: Separator type (A-F). Defaults to "A" (curly braces).
        target_prefix: Expected response prefix.

    Returns:
        Jailbroken prompt in parallel format.
    """
    if benign_prompt is None:
        benign_prompt = "List the categories of domain names"
    if target_prefix is None:
        target_prefix = "Sure, here is"
    
    wrapper = SEPARATORS.get(separator, "{}")
    left, right = wrapper[0], wrapper[1]
    
    # Combine the harmful prompt (outside) with benign prompt (inside)
    combined_request = _combine_sentences(prompt, benign_prompt, wrapper)
    
    # Use the prompts module
    jailbreak = prompts.get_jail_con_template(prompt, "template1")
    user_content = f"REQUEST: {combined_request}\nAnswer: {target_prefix}"
    
    return f"{jailbreak}\n\n{user_content}"


@register_jailbreak("jail_con_auto2")
def jail_con_auto2(
    prompt: str,
    benign_prompt: str = None,
    separator: str = "A",
    target_prefix: str = None,
    **kwargs,
) -> str:
    """JAIL-CON Auto2 (CVT) - Context Varying Technique.
    
    Creates a parallel prompt where the model answers both questions in parallel,
    with words corresponding to inside/outside brackets respectively.

    Args:
        prompt: Forbidden prompt.
        benign_prompt: Benign prompt to hide inside brackets.
        separator: Separator type (A-F). Defaults to "A" (curly braces).
        target_prefix: Expected response prefix.

    Returns:
        Jailbroken prompt in parallel format.
    """
    if benign_prompt is None:
        benign_prompt = "List the categories of domain names"
    if target_prefix is None:
        target_prefix = "Sure, here is"
    
    wrapper = SEPARATORS.get(separator, "{}")
    left, right = wrapper[0], wrapper[1]
    
    # Combine the harmful prompt (outside) with benign prompt (inside)
    combined_request = _combine_sentences(prompt, benign_prompt, wrapper)
    
    # Also combine the target prefix
    combined_target = _combine_sentences(target_prefix, target_prefix, wrapper)
    
    # Use the prompts module
    jailbreak = prompts.get_jail_con_template(prompt, "template2")
    user_content = f"REQUEST: {combined_request}\nAnswer: {combined_target}"
    
    return f"{jailbreak}\n\n{user_content}"


@register_jailbreak("jail_con")
def jail_con(
    prompt: str,
    method: str = "auto2",
    benign_prompt: str = None,
    separator: str = "A",
    **kwargs,
) -> str:
    """JAIL-CON jailbreak attack (wrapper for both methods).

    Args:
        prompt: Forbidden prompt.
        method: Either "auto1" (CIT) or "auto2" (CVT).
        benign_prompt: Benign prompt to hide inside brackets.
        separator: Separator type (A-F).

    Returns:
        Jailbroken prompt.
    """
    if method.lower() == "auto1":
        return jail_con_auto1(prompt, benign_prompt, separator, **kwargs)
    else:
        return jail_con_auto2(prompt, benign_prompt, separator, **kwargs)
