"""
DeepInception Jailbreak Attack

Uses nested storytelling and scene-setting to bypass safety mechanisms.

Reference:
    @article{li2023deepinception,
        title={DeepInception: Hypnotize Large Language Model to Be Jailbreaker},
        author={Li, Xuan and Zhou, Zhanke and Zhu, Jianing and Yong, Jiangchao and Wang, Yiran and He, Ran and Feng, Bo},
        journal={arXiv preprint arXiv:2311.03191},
        year={2023}
    }
"""

import random
from ..registry import register_jailbreak
from . import prompts

# Define scenes and character types
SCENES = ["science fiction", "fantasy world", "mystery novel", "historical drama"]
CHARACTER_TYPES = ["scientists", "hackers", "detectives", "explorers"]


@register_jailbreak("deep_inception")
def deep_inception(
    prompt: str,
    n_layers: int = 5,
    n_characters: int = 5,
    scene: str = "science fiction",
    lang: str = "en",
    seed: int = None,
    **kwargs,
) -> str:
    """DeepInception jailbreak attack.
    
    Creates nested storytelling layers to embed the harmful request.

    Args:
        prompt: Forbidden prompt (the "goal"). Can be a string or list (first element used).
        n_layers: Number of nested layers.
        n_characters: Number of characters in each layer.
        scene: Scene type for the story.
        lang: Language for the output.
        seed: Random seed.

    Returns:
        Jailbroken prompt using deep inception technique.
    """
    rng = random.Random(seed)
    
    # Handle both string and list inputs
    if isinstance(prompt, list):
        prompt = prompt[0] if prompt else ""
    
    # Use multi-layer inception from prompts module
    jailbreak_prompt = prompts.get_multi_layer_inception(prompt, n_layers, language=lang)
    
    return jailbreak_prompt


@register_jailbreak("deep_inception_simple")
def deep_inception_simple(
    prompt: str,
    **kwargs,
) -> str:
    """Simplified DeepInception using default parameters.
    
    Args:
        prompt: Forbidden prompt.
        
    Returns:
        Jailbroken prompt.
    """
    return deep_inception(prompt, n_layers=3, n_characters=3, scene="science fiction", **kwargs)


@register_jailbreak("deep_inception_story")
def deep_inception_story(
    prompt: str,
    seed: int = None,
    **kwargs,
) -> str:
    """DeepInception variant with random scene selection.
    
    Args:
        prompt: Forbidden prompt.
        seed: Random seed.
        
    Returns:
        Jailbroken prompt with random scene.
    """
    rng = random.Random(seed)
    scene = rng.choice(SCENES)
    n_layers = rng.randint(3, 6)
    n_characters = rng.randint(3, 7)
    
    return deep_inception(prompt, n_layers, n_characters, scene, seed=seed, **kwargs)
