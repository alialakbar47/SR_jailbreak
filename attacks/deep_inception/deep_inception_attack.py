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
import pathlib
from ..registry import register_jailbreak

# Load prompts from file
PROMPTS_FILE = pathlib.Path(__file__).parent / "prompts.txt"


def _load_prompts() -> dict:
    """Load prompt templates from prompts.txt file."""
    prompts = {}
    try:
        with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        current_key = None
        current_content = []
        
        for line in content.split("\n"):
            if line.startswith("### "):
                if current_key:
                    prompts[current_key] = "\n".join(current_content).strip()
                current_key = line[4:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_key:
            prompts[current_key] = "\n".join(current_content).strip()
        
        return prompts
    except FileNotFoundError:
        return {
            "main_template": "Create a {scene} with {n_characters} characters across {n_layers} layers. Goal: {goal}",
            "scenes": "science fiction\nfantasy world",
            "character_types": "scientists\nhackers",
        }


# Load prompts
PROMPTS = _load_prompts()


def _get_scenes() -> list:
    """Get available scenes from prompts."""
    if "scenes" in PROMPTS:
        return [s.strip() for s in PROMPTS["scenes"].split("\n") if s.strip()]
    return ["science fiction", "fantasy world"]


def _get_character_types() -> list:
    """Get available character types from prompts."""
    if "character_types" in PROMPTS:
        return [c.strip() for c in PROMPTS["character_types"].split("\n") if c.strip()]
    return ["scientists", "hackers"]


SCENES = _get_scenes()
CHARACTER_TYPES = _get_character_types()


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
        prompt: Forbidden prompt (the "goal").
        n_layers: Number of nested layers.
        n_characters: Number of characters in each layer.
        scene: Scene type for the story.
        lang: Language for the output.
        seed: Random seed.

    Returns:
        Jailbroken prompt using deep inception technique.
    """
    rng = random.Random(seed)
    
    # Use the template with the goal
    template = PROMPTS.get("main_template", "Create a scenario where characters must {goal}")
    
    jailbreak_prompt = template.format(
        scene=scene,
        n_characters=n_characters,
        n_layers=n_layers,
        goal=prompt
    )
    
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
