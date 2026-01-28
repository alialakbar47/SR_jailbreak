"""
ReNeLLM (Rewrite and Nest) Jailbreak Attack

Uses rewriting and nesting to bypass content filters.

Reference:
    @article{ding2023wolf,
        title={A Wolf in Sheep's Clothing: Generalized Nested Jailbreak Prompts can Fool Large Language Models Easily},
        author={Ding, Peng and Kuang, Jun and Ma, Dan and Cao, Xuezhi and Xian, Yunsen and Chen, Jiajun and Huang, Shujian},
        journal={arXiv preprint arXiv:2311.08268},
        year={2023}
    }
"""

import random
import warnings

from ..registry import register_jailbreak
from . import prompts


@register_jailbreak("renellm")
def renellm(
    prompt: str,
    model: str = "gemma-3-27b-it",
    use_llm: bool = False,
    scenario: str = None,
    seed: int = None,
    verbose: bool = False,
    language: str = "english",
    **kwargs,
) -> str:
    """ReNeLLM jailbreak attack.
    
    Rewrites and nests the prompt in a legitimate context.

    Args:
        prompt: Forbidden prompt.
        model: Model to use for rewriting.
        use_llm: Whether to use LLM for rewriting.
        scenario: Scenario template to use (research, fiction, education, journalism).
        seed: Random seed.
        verbose: If True, print LLM interactions. Defaults to False.

    Returns:
        Jailbroken prompt.
    """
    rng = random.Random(seed)
    
    if scenario is None:
        scenario = rng.choice(list(prompts.SCENARIO_TEMPLATES.keys())) if prompts.SCENARIO_TEMPLATES else "research"
    
    if use_llm:
        from ...generate import generate_response as generate
        
        # First rewrite
        rewrite_request = prompts.get_rewrite_prompt(forbidden_prompt=prompt, language=language)
        rewritten = generate(rewrite_request, model, max_tokens=200, verbose=verbose)
        
        # Then nest
        nest_request = prompts.get_nest_prompt(forbidden_prompt=rewritten, language=language)
        nested = generate(nest_request, model, max_tokens=300, verbose=verbose)
        
        return nested
    else:
        # Use template-based nesting
        template = prompts.get_scenario_template(scenario)
        # Extract topic from prompt
        words = prompt.split()
        topic = " ".join(words[:3]) if len(words) > 3 else prompt
        
        return template.format(forbidden_prompt=prompt, topic=topic)


@register_jailbreak("renellm_research")
def renellm_research(prompt: str, **kwargs) -> str:
    """ReNeLLM with research framing."""
    return renellm(prompt, scenario="research", **kwargs)


@register_jailbreak("renellm_fiction")
def renellm_fiction(prompt: str, **kwargs) -> str:
    """ReNeLLM with fiction framing."""
    return renellm(prompt, scenario="fiction", **kwargs)


@register_jailbreak("renellm_education")
def renellm_education(prompt: str, **kwargs) -> str:
    """ReNeLLM with education framing."""
    return renellm(prompt, scenario="education", **kwargs)
