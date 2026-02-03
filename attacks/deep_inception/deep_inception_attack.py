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
    target_model: str = "gemma-3-27b-it",
    evaluator: str = None,
    depth: int = 5,
    n_characters: int = 5,
    scene: str = "science fiction",
    language: str = "english",
    seed: int = None,
    verbose: bool = False,
    max_tokens: int = 1024,
    **kwargs,
) -> dict:
    """DeepInception jailbreak attack.
    
    Creates nested storytelling layers to embed the harmful request,
    sends it to the target model, and returns the model's response.

    Args:
        prompt: Forbidden prompt (the "goal"). Can be a string or list (first element used).
        target_model: Target model to attack.
        evaluator: Optional evaluator to judge success.
        depth: Number of nested layers.
        n_characters: Number of characters in each layer.
        scene: Scene type for the story.
        language: Language for the output ("english" or "arabic").
        seed: Random seed.
        verbose: Print progress information.
        max_tokens: Maximum tokens for model response.

    Returns:
        Dictionary containing jailbreak prompt and model response.
    """
    try:
        from ...generate import generate_response as generate
    except ImportError:
        from ..generate import generate_response as generate
    
    rng = random.Random(seed)
    
    # Handle both string and list inputs
    if isinstance(prompt, list):
        prompt = prompt[0] if prompt else ""
    
    if verbose:
        print(f"\n🎯 Starting Deep Inception Attack")
        print(f"Goal: {prompt}")
        print(f"Depth: {depth} layers")
        print(f"Language: {language}\n")
    
    # Generate the jailbreak prompt using multi-layer inception
    jailbreak_prompt = prompts.get_multi_layer_inception(prompt, depth, language=language)
    
    if verbose:
        print(f"✅ Generated jailbreak prompt ({len(jailbreak_prompt)} chars)")
        print(f"Preview: {jailbreak_prompt[:200]}...\n")
        print(f"🎯 Sending to target model ({target_model})...")
    
    # Send jailbreak to target model and get response
    model_response = generate(jailbreak_prompt, target_model, max_tokens=max_tokens, verbose=verbose)
    
    if verbose:
        print(f"\n✅ Received response ({len(model_response)} chars)")
        print(f"Response preview: {model_response[:200]}...")
    
    result = {
        "goal": prompt,
        "jailbreak_prompt": jailbreak_prompt,
        "response": model_response,
        "model": target_model,
        "depth": depth,
        "language": language,
        "scene": scene
    }
    
    return result


@register_jailbreak("deep_inception_simple")
def deep_inception_simple(
    prompt: str,
    **kwargs,
) -> dict:
    """Simplified DeepInception using default parameters.
    
    Args:
        prompt: Forbidden prompt.
        
    Returns:
        Dictionary with jailbreak prompt and model response.
    """
    return deep_inception(prompt, depth=3, n_characters=3, scene="science fiction", **kwargs)


@register_jailbreak("deep_inception_story")
def deep_inception_story(
    prompt: str,
    seed: int = None,
    **kwargs,
) -> dict:
    """DeepInception variant with random scene selection.
    
    Args:
        prompt: Forbidden prompt.
        seed: Random seed.
        
    Returns:
        Dictionary with jailbreak prompt and model response.
    """
    rng = random.Random(seed)
    scene = rng.choice(SCENES)
    depth = rng.randint(3, 6)
    n_characters = rng.randint(3, 7)
    
    return deep_inception(prompt, depth=depth, n_characters=n_characters, scene=scene, seed=seed, **kwargs)
