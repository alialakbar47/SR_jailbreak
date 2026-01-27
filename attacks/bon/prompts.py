"""BON (Best-of-N) attack prompt templates."""


def get_bon_instruction(prompt):
    """
    BON doesn't modify the prompt - it generates multiple responses
    and selects the one most likely to violate safety guidelines.
    """
    return prompt
