"""
PAP (Persuasive Adversarial Prompts) Jailbreak Attack

Reference:
    @article{zeng2024johnny,
        title={How johnny can persuade llms to jailbreak them: Rethinking persuasion to challenge ai safety by humanizing llms},
        author={Zeng, Yi and Lin, Hongpeng and Zhang, Jingwen and Yang, Diyi and Jia, Ruoxi and Shi, Weiyan},
        journal={arXiv preprint arXiv:2401.06373},
        year={2024}
    }
"""

import warnings
from functools import partial

from ..registry import register_jailbreak, registered_jailbreaks
from . import prompts


def pap(
    prompt: str,
    template: str,
    models: tuple = ("google/gemini-1.5-flash", "openai/gpt-4o-mini"),
    max_tokens: int = 200,
    verbose: bool = False,
    **kwargs,
) -> str:
    """PAP (Persuasive Adversarial Prompts) jailbreak.

    Uses persuasion techniques to rewrite the prompt.

    Args:
        prompt: Forbidden prompt.
        template: Template key for the persuasion technique.
        models: Models to generate the rewritten prompt. Falls back to next on failure.
        max_tokens: Maximum tokens to generate.
        verbose: If True, print LLM interactions. Defaults to False.

    Returns:
        Jailbroken prompt using persuasion techniques.
    """
    from ...generate import generate_response as generate
    
    pap_prompt = prompts.PERSUASION_TECHNIQUES[template](prompt)
    start_phrase = "#mutated_text_with_same_specific_harmful_or_unlawful_intention: "
    
    for model in models:
        response = generate(pap_prompt, model, max_tokens=max_tokens, verbose=verbose)
        try:
            index = response.index(start_phrase)
            return response[index + len(start_phrase):]
        except:
            continue

    msg = f"PAP template {template} failed to generate a jailbroken prompt for {prompt}"
    warnings.warn(msg)
    return prompt


# Register all PAP variants
for template_name in prompts.PERSUASION_TECHNIQUES:
    registered_jailbreaks[f"pap_{template_name}"] = partial(pap, template=template_name)
