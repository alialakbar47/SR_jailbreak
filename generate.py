"""
Multi-Provider LLM Generation Module

Supports:
- Google Gemini (via google-generativeai)
- OpenAI
- Anthropic
- Local HuggingFace models
"""

import time
import warnings
import multiprocessing
from typing import Union, Optional, List, Dict, Any

from datasets import Dataset, concatenate_datasets

# Provider detection and loading
def _detect_provider(model: str) -> str:
    """Detect the provider from model string."""
    if model.startswith("google/") or model.startswith("gemini"):
        return "google"
    elif model.startswith("openai/") or model.startswith("gpt"):
        return "openai"
    elif model.startswith("anthropic/") or model.startswith("claude"):
        return "anthropic"
    elif model.startswith("huggingface/") or model.startswith("hf/"):
        return "huggingface"
    else:
        # Default to OpenAI-compatible API (litellm)
        return "litellm"


def _generate_google(
    messages: List[Dict[str, str]],
    model: str,
    temperature: float = 1.0,
    max_tokens: int = 1024,
    **kwargs
) -> str:
    """Generate response using Google Gemini API."""
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("Please install google-generativeai: pip install google-generativeai")
    
    # Extract model name (remove prefix if present)
    model_name = model.replace("google/", "")
    
    # Check if this is a Gemma model (they don't support system_instruction)
    is_gemma = "gemma" in model_name.lower()
    
    # Configure generation
    generation_config = genai.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    
    # Convert messages to Gemini format
    gemini_messages = []
    system_instruction = None
    
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        
        if role == "system":
            system_instruction = content
        elif role == "user":
            gemini_messages.append({"role": "user", "parts": [content]})
        elif role == "assistant":
            gemini_messages.append({"role": "model", "parts": [content]})
    
    # Handle system instruction based on model type
    if system_instruction:
        if is_gemma:
            # Gemma models don't support system_instruction, prepend to first user message
            if gemini_messages and gemini_messages[0]["role"] == "user":
                original_content = gemini_messages[0]["parts"][0]
                gemini_messages[0]["parts"][0] = f"[System Instructions]\n{system_instruction}\n\n[User Message]\n{original_content}"
            genai_model = genai.GenerativeModel(model_name, generation_config=generation_config)
        else:
            # Other models (Gemini) support system_instruction
            genai_model = genai.GenerativeModel(
                model_name, 
                generation_config=generation_config,
                system_instruction=system_instruction
            )
    else:
        genai_model = genai.GenerativeModel(model_name, generation_config=generation_config)
    
    # Generate response
    if len(gemini_messages) == 1:
        response = genai_model.generate_content(gemini_messages[0]["parts"][0])
    else:
        chat = genai_model.start_chat(history=gemini_messages[:-1])
        response = chat.send_message(gemini_messages[-1]["parts"][0])
    
    return response.text


def _generate_openai(
    messages: List[Dict[str, str]],
    model: str,
    temperature: float = 1.0,
    max_tokens: int = 1024,
    **kwargs
) -> str:
    """Generate response using OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Please install openai: pip install openai")
    
    # Extract model name (remove prefix if present)
    model_name = model.replace("openai/", "")
    
    client = OpenAI()
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
    
    return response.choices[0].message.content


def _generate_anthropic(
    messages: List[Dict[str, str]],
    model: str,
    temperature: float = 1.0,
    max_tokens: int = 1024,
    **kwargs
) -> str:
    """Generate response using Anthropic API."""
    try:
        import anthropic
    except ImportError:
        raise ImportError("Please install anthropic: pip install anthropic")
    
    # Extract model name (remove prefix if present)
    model_name = model.replace("anthropic/", "")
    
    client = anthropic.Anthropic()
    
    # Extract system message if present
    system_prompt = None
    filtered_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_prompt = msg["content"]
        else:
            filtered_messages.append(msg)
    
    response = client.messages.create(
        model=model_name,
        max_tokens=max_tokens,
        system=system_prompt if system_prompt else "",
        messages=filtered_messages,
        temperature=temperature,
        **kwargs
    )
    
    return response.content[0].text


def _generate_huggingface(
    messages: List[Dict[str, str]],
    model: str,
    temperature: float = 1.0,
    max_tokens: int = 1024,
    **kwargs
) -> str:
    """Generate response using HuggingFace transformers."""
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        import torch
    except ImportError:
        raise ImportError("Please install transformers: pip install transformers torch")
    
    # Extract model name (remove prefix if present)
    model_name = model.replace("huggingface/", "").replace("hf/", "")
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model_hf = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    )
    
    # Create pipeline
    pipe = pipeline(
        "text-generation",
        model=model_hf,
        tokenizer=tokenizer,
        max_new_tokens=max_tokens,
        temperature=temperature if temperature > 0 else None,
        do_sample=temperature > 0,
    )
    
    # Generate
    result = pipe(messages)
    return result[0]["generated_text"][-1]["content"]


def _generate_litellm(
    messages: List[Dict[str, str]],
    model: str,
    temperature: float = 1.0,
    max_tokens: int = 1024,
    **kwargs
) -> str:
    """Generate response using LiteLLM (fallback for various providers)."""
    try:
        from litellm import completion
    except ImportError:
        raise ImportError("Please install litellm: pip install litellm")
    
    response = completion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
    
    return response.choices[0].message.content


def convert_to_messages(
    prompt: Union[str, List[str], List[Dict[str, str]]], 
    system_prompt: Optional[str] = None
) -> List[Dict[str, str]]:
    """Convert a prompt to messages format for generating a response.

    Args:
        prompt: Input to convert to messages format. If a string, this is treated 
            as the user content. If a list of strings, these are treated as 
            alternating user and assistant content. The input may also already 
            be in messages format.
        system_prompt: System prompt. Defaults to None.

    Returns:
        List of messages, where a message is {"role": <role>, "content": <content>}.
    """
    if isinstance(prompt, str):
        messages = [{"role": "user", "content": prompt}]
    elif isinstance(prompt[0], str):
        messages = []
        for i, content in enumerate(prompt):
            messages.append({"role": "user" if i % 2 == 0 else "assistant", "content": content})
    else:
        messages = prompt

    if system_prompt is not None:
        if messages[0]["role"] == "system":
            messages[0]["content"] = system_prompt
        else:
            messages = [{"role": "system", "content": system_prompt}] + messages

    return messages


def generate_response(
    prompt: Union[str, List[str], List[Dict[str, str]]],
    model: str,
    system_prompt: Optional[str] = None,
    num_retries: int = 5,
    delay: float = 0,
    temperature: float = 1.0,
    max_tokens: int = 1024,
    verbose: bool = False,
    **kwargs,
) -> str:
    """Call an LLM to generate a response.

    Supports multiple providers:
    - Google Gemini: prefix with "google/" or use "gemini-*"
    - OpenAI: prefix with "openai/" or use "gpt-*"
    - Anthropic: prefix with "anthropic/" or use "claude-*"
    - HuggingFace: prefix with "huggingface/" or "hf/"
    - Other: Falls back to LiteLLM

    Args:
        prompt: Prompt to respond to. See convert_to_messages for valid formats.
        model: Model identifier with optional provider prefix.
        system_prompt: System prompt. Defaults to None.
        num_retries: Number of retries if an error is encountered. Defaults to 5.
        delay: Initial delay before calling the API. Defaults to 0.
        temperature: Sampling temperature. Defaults to 1.0.
        max_tokens: Maximum tokens to generate. Defaults to 1024.
        verbose: If True, print all prompts and responses. Defaults to False.
        **kwargs: Additional provider-specific arguments.

    Returns:
        str: Response.
    """
    if num_retries == 0:
        msg = f"Failed to get response from model {model} for prompt {prompt}"
        warnings.warn(msg)
        return ""

    messages = convert_to_messages(prompt, system_prompt=system_prompt)
    provider = _detect_provider(model)
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"🤖 LLM CALL: {model} (provider: {provider})")
        print(f"{'='*80}")
        for i, msg in enumerate(messages):
            role_emoji = {"system": "⚙️", "user": "👤", "assistant": "🤖"}.get(msg["role"], "💬")
            print(f"{role_emoji} {msg['role'].upper()}:")
            print(f"{msg['content'][:500]}{'...' if len(msg['content']) > 500 else ''}")
            print(f"{'-'*80}")
    
    # Provider-specific generation functions
    generators = {
        "google": _generate_google,
        "openai": _generate_openai,
        "anthropic": _generate_anthropic,
        "huggingface": _generate_huggingface,
        "litellm": _generate_litellm,
    }
    
    generator_func = generators.get(provider, _generate_litellm)

    for attempt in range(num_retries):
        if delay > 0:
            time.sleep(delay)

        try:
            response = generator_func(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            if response is not None:
                if verbose:
                    print(f"✅ RESPONSE:")
                    print(f"{response[:500]}{'...' if len(response) > 500 else ''}")
                    print(f"{'='*80}\n")
                return response
        except Exception as e:
            print(f"Attempt {attempt + 1}/{num_retries} failed: {e}")

        delay = 1 if delay == 0 else (2 * delay)

    return ""


# Backward compatibility alias
generate = generate_response


def generate_to_dataset(
    dataset: Dataset,
    models: List[str],
    target_column: str = "prompt",
    decode_responses: bool = True,
    num_processes: int = None,
    **kwargs,
) -> Dataset:
    """Generate responses to a HuggingFace dataset of prompts.

    Args:
        dataset: Dataset with prompts.
        models: Models used to generate responses.
        target_column: Column that the models should use as the prompt. Defaults to "prompt".
        decode_responses: Decode the raw responses. Defaults to True.
        num_processes: Number of processes to use for generating responses. 
            Defaults to the number of CPUs.
        **kwargs: Additional arguments passed to generate().

    Returns:
        Dataset: Dataset with responses.
    """
    if num_processes is None:
        num_processes = multiprocessing.cpu_count()
    
    generated_datasets = []
    
    for model in models:
        generated_dataset = dataset.map(
            lambda x: {"response": generate(x[target_column], model, **kwargs)},
            num_proc=num_processes,
        )
        generated_dataset = generated_dataset.add_column(
            "model", len(generated_dataset) * [model]
        )
        generated_datasets.append(generated_dataset)

    dataset = concatenate_datasets(generated_datasets)
    
    if decode_responses:
        from .jailbreaks import decode_dataset
        dataset = decode_dataset(dataset)

    return dataset
