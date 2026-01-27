"""
Translation Jailbreak Attack

Uses low-resource language translation to bypass content filters.

Reference:
    @article{yong2023low,
        title={Low-resource languages jailbreak GPT-4},
        author={Yong, Zheng-Xin and Menghini, Cristina and Bach, Stephen H},
        journal={arXiv preprint arXiv:2310.02446},
        year={2023}
    }
"""

from functools import partial

from ..registry import register_jailbreak, registered_jailbreaks
from . import prompts


def translation(prompt: str, language: str, **kwargs) -> str:
    """Translation jailbreak using low-resource languages.

    Args:
        prompt: Forbidden prompt.
        language: Target language name.

    Returns:
        Jailbroken prompt requesting translation.
    """
    return prompts.get_translate_request(language=language, forbidden_prompt=prompt)


# Register translation jailbreaks for each language
for lang_key, lang_name in prompts.LANGUAGES.items():
    registered_jailbreaks[f"translate_{lang_key}"] = partial(translation, language=lang_name)
