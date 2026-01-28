"""
GPTFuzzer Jailbreak Attack

Based on the GPTFUZZER method that uses genetic mutation to generate jailbreak prompts.

Reference:
    @article{yu2023gptfuzzer,
        title={GPTFUZZER: Red Teaming Large Language Models with Auto-Generated Jailbreak Prompts},
        author={Yu, Jiahao and Lin, Xingwei and Yu, Zheng and Xing, Xinyu},
        journal={arXiv preprint arXiv:2309.10253},
        year={2023}
    }
"""

import random
import warnings
from ..registry import register_jailbreak
from . import prompts


def _mutation_expand(prompt: str, model: str, language: str = "english", **kwargs) -> str:
    """Expand the prompt with more details."""
    from ...generate import generate_response as generate
    
    expand_prompt = prompts.get_mutation_expand(prompt=prompt, language=language)
    return generate(expand_prompt, model, max_tokens=500, **kwargs)


def _mutation_shorten(prompt: str, model: str, language: str = "english", **kwargs) -> str:
    """Shorten the prompt while keeping the meaning."""
    from ...generate import generate_response as generate
    
    shorten_prompt = prompts.get_mutation_shorten(prompt=prompt, language=language)
    return generate(shorten_prompt, model, max_tokens=300, **kwargs)


def _mutation_rephrase(prompt: str, model: str, language: str = "english", **kwargs) -> str:
    """Rephrase the prompt."""
    from ...generate import generate_response as generate
    
    rephrase_prompt = prompts.get_mutation_rephrase(prompt=prompt, language=language)
    return generate(rephrase_prompt, model, max_tokens=500, **kwargs)


def _mutation_crossover(prompt1: str, prompt2: str) -> str:
    """Combine two prompts."""
    lines1 = prompt1.split('\n')
    lines2 = prompt2.split('\n')
    
    # Simple crossover: take first half from prompt1, second half from prompt2
    mid = len(lines1) // 2
    result_lines = lines1[:mid] + lines2[mid:]
    
    return '\n'.join(result_lines)


@register_jailbreak("gptfuzzer")
def gptfuzzer(
    prompt: str,
    attack_model: str = "gemma-3-27b-it",
    victim_model: str = "gemma-3-27b-it",
    max_iterations: int = 10,
    population_size: int = 5,
    seed: int = None,
    language: str = "english",
    **kwargs,
) -> str:
    """GPTFuzzer jailbreak attack.
    
    Uses genetic mutation to evolve jailbreak prompts.

    Args:
        prompt: Forbidden prompt.
        attack_model: Model to generate mutations.
        victim_model: Model to test jailbreak success.
        max_iterations: Maximum number of evolution iterations.
        population_size: Number of prompts in the population.
        seed: Random seed.

    Returns:
        Best jailbroken prompt found.
    """
    from ...generate import generate_response as generate
    from ...evaluators.registry import evaluate_response as evaluate
    
    rng = random.Random(seed)
    
    # Initialize population with seed templates
    population = []
    for template in rng.sample(prompts.SEED_TEMPLATES, min(population_size, len(prompts.SEED_TEMPLATES))):
        jailbreak_prompt = template.replace("[INSERT PROMPT HERE]", prompt)
        population.append(jailbreak_prompt)
    
    # Fill remaining slots
    while len(population) < population_size:
        template = rng.choice(prompts.SEED_TEMPLATES)
        jailbreak_prompt = template.replace("[INSERT PROMPT HERE]", prompt)
        population.append(jailbreak_prompt)
    
    best_prompt = population[0]
    best_score = 0
    
    mutations = [
        lambda p, m, **kw: _mutation_expand(p, m, language=language, **kw),
        lambda p, m, **kw: _mutation_shorten(p, m, language=language, **kw),
        lambda p, m, **kw: _mutation_rephrase(p, m, language=language, **kw)
    ]
    
    for iteration in range(max_iterations):
        # Evaluate population
        scores = []
        for jb_prompt in population:
            try:
                response = generate(jb_prompt, victim_model, max_tokens=200, **kwargs)
                result = evaluate("string_matching", prompt, response)
                score = result.get("score", 0)
                scores.append(score)
                
                if score > best_score:
                    best_score = score
                    best_prompt = jb_prompt
                    
                if score == 1.0:  # Perfect jailbreak
                    return jb_prompt
            except:
                scores.append(0)
        
        # Selection: keep top half
        sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        survivors = [population[i] for i in sorted_indices[:population_size // 2]]
        
        # Generate new population through mutation
        new_population = survivors.copy()
        while len(new_population) < population_size:
            parent = rng.choice(survivors)
            mutation = rng.choice(mutations)
            try:
                child = mutation(parent, attack_model, **kwargs)
                # Re-insert the forbidden prompt
                if "[INSERT PROMPT HERE]" not in child:
                    child = child + f"\n\nNow answer this: {prompt}"
                new_population.append(child)
            except:
                new_population.append(parent)
        
        population = new_population
    
    return best_prompt


@register_jailbreak("gptfuzzer_simple")
def gptfuzzer_simple(prompt: str, seed: int = None, **kwargs) -> str:
    """Simple GPTFuzzer that just uses a random seed template.
    
    Args:
        prompt: Forbidden prompt.
        seed: Random seed.
        
    Returns:
        Jailbroken prompt using a seed template.
    """
    rng = random.Random(seed)
    template = rng.choice(prompts.SEED_TEMPLATES)
    return template.replace("[INSERT PROMPT HERE]", prompt)
