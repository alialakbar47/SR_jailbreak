"""
Best-of-N (BoN) Jailbreak Attack

Applies random perturbations to prompts to find successful jailbreaks.

Reference:
    @article{hughes2024best,
        title={Best-of-n jailbreaking},
        author={Hughes, John and Price, Sara and Lynch, Aengus and others},
        journal={arXiv preprint arXiv:2412.03556},
        year={2024}
    }
"""

import random

from ..registry import register_jailbreak
from . import prompts

# Define perturbation types
PERTURBATION_TYPES = ["uppercase", "lowercase", "leetspeak", "random_case", "title", "add_typos"]


def _apply_perturbation(text: str, perturbation: str, rng: random.Random) -> str:
    """Apply a single perturbation to text."""
    if perturbation == "uppercase":
        return text.upper()
    elif perturbation == "lowercase":
        return text.lower()
    elif perturbation == "title":
        return text.title()
    elif perturbation == "random_case":
        return "".join(c.upper() if rng.random() > 0.5 else c.lower() for c in text)
    elif perturbation == "leetspeak":
        leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
        return "".join(leet_map.get(c.lower(), c) for c in text)
    elif perturbation == "add_typos":
        chars = list(text)
        for _ in range(max(1, len(chars) // 20)):
            if chars:
                idx = rng.randint(0, len(chars) - 1)
                chars[idx] = rng.choice('abcdefghijklmnopqrstuvwxyz')
        return "".join(chars)
    elif perturbation == "add_spaces":
        return " ".join(text)
    elif perturbation == "remove_spaces":
        words = text.split()
        result = []
        for i, word in enumerate(words):
            result.append(word)
            if rng.random() > 0.5:
                result.append("")
        return " ".join(result)
    return text


@register_jailbreak("bon")
def bon(
    prompt: str,
    n: int = 10,
    perturbations: list = None,
    seed: int = None,
    **kwargs,
) -> str:
    """Best-of-N jailbreak attack.
    
    Generates multiple perturbations and returns the best one.

    Args:
        prompt: Forbidden prompt.
        n: Number of perturbations to try.
        perturbations: List of perturbation types to apply.
        seed: Random seed.

    Returns:
        Perturbed prompt.
    """
    rng = random.Random(seed)
    
    if perturbations is None:
        perturbations = PERTURBATION_TYPES
    
    # Generate n perturbed versions
    candidates = []
    for _ in range(n):
        perturbed = prompt
        # Apply 1-3 random perturbations
        num_perturbations = rng.randint(1, min(3, len(perturbations)))
        for perturbation in rng.sample(perturbations, num_perturbations):
            perturbed = _apply_perturbation(perturbed, perturbation, rng)
        candidates.append(perturbed)
    
    # Return a random candidate (in full implementation, would evaluate and pick best)
    # Use prompts module to get final instruction
    chosen = rng.choice(candidates)
    return prompts.get_bon_instruction(chosen)


@register_jailbreak("bon_single")
def bon_single(prompt: str, perturbation: str = "random_case", seed: int = None, **kwargs) -> str:
    """Apply a single perturbation.
    
    Args:
        prompt: Forbidden prompt.
        perturbation: Perturbation type.
        seed: Random seed.
        
    Returns:
        Perturbed prompt.
    """
    rng = random.Random(seed)
    return _apply_perturbation(prompt, perturbation, rng)
