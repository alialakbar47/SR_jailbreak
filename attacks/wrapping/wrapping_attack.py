"""
Wrapping Jailbreak Attacks

Template-based jailbreaks that wrap the forbidden prompt in various contexts.

References:
    - Combination attacks, distractors, style injection, etc.: Wei et al. (2023)
    - GCG (HarmBench): Mazeika et al. (2024)
    - GCG (Universal Attacks): Zou et al. (2023)
    - AIM, dev mode, evil confidant: jailbreakchat.com
"""

import base64
import json
import pathlib
from functools import partial

from ..registry import register_jailbreak, register_decoder, registered_jailbreaks, registered_decoders

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
        return {"none": "{forbidden_prompt}"}


# Load prompts
TEMPLATES = _load_prompts()


def wrapping_jailbreak(prompt: str, jailbreak: str, **kwargs) -> str:
    """Apply a wrapping jailbreak to a prompt.

    Args:
        prompt: Forbidden prompt.
        jailbreak: Jailbreak template name.

    Returns:
        Jailbroken prompt.
    """
    template = TEMPLATES.get(jailbreak, "{forbidden_prompt}")
    
    # Base64 encode for certain jailbreaks
    if jailbreak.startswith("combination"):
        encoded_prompt = base64.b64encode(prompt.encode("utf-8")).decode()
        return template.replace("{forbidden_prompt}", encoded_prompt)
    
    return template.replace("{forbidden_prompt}", prompt)


def decode_json_list(response: str) -> str:
    """Decode a JSON list response."""
    if response.startswith("```json"):
        response = response[7:]
    if response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]
    
    try:
        parsed = json.loads(response)
        if isinstance(parsed, list):
            return " ".join(parsed)
    except:
        pass
    
    return response


# Register all wrapping jailbreaks
for template_name in TEMPLATES:
    registered_jailbreaks[template_name] = partial(wrapping_jailbreak, jailbreak=template_name)

# Register decoders for JSON-based jailbreaks
for template_name in ["style_injection_json", "few_shot_json", "combination_2", "combination_3"]:
    if template_name in TEMPLATES:
        registered_decoders[template_name] = decode_json_list
