"""
Attack Registry Module

Provides registration and management of jailbreak attacks.
"""

import multiprocessing
from typing import Callable, Dict, List
from functools import partial

from datasets import Dataset, concatenate_datasets

# Global registries
registered_jailbreaks: Dict[str, Callable] = {}
registered_decoders: Dict[str, Callable] = {}


def register_jailbreak(key: str) -> Callable:
    """Register a new jailbreak.

    Args:
        key: Jailbreak name.

    Returns:
        Callable: Decorator function.
    """
    def inner(func):
        registered_jailbreaks[key] = func
        return func
    return inner


def register_decoder(key: str) -> Callable:
    """Register a new decoder.

    Args:
        key: Decoder name (typically matches jailbreak name).

    Returns:
        Callable: Decorator function.
    """
    def inner(func):
        registered_decoders[key] = func
        return func
    return inner


def apply_jailbreaks(prompt: str, jailbreaks: List[str], **kwargs) -> List[str]:
    """Apply jailbreaks to a forbidden prompt.

    Args:
        prompt: Forbidden prompt.
        jailbreaks: List of jailbreaks to apply.
        **kwargs: Additional arguments passed to jailbreak functions.

    Returns:
        List of jailbroken prompts.
    """
    return [registered_jailbreaks[jailbreak](prompt, **kwargs) for jailbreak in jailbreaks]


def apply_jailbreaks_to_dataset(
    dataset: Dataset, 
    jailbreaks: List[str], 
    **kwargs
) -> Dataset:
    """Apply jailbreaks to a HuggingFace dataset with forbidden prompts.

    Args:
        dataset: Dataset with forbidden prompts in 'forbidden_prompt' column.
        jailbreaks: List of jailbreaks to apply.
        **kwargs: Additional arguments passed to jailbreak functions.

    Returns:
        Dataset with jailbroken prompts.
    """
    from ..generate import convert_to_messages
    
    jailbroken_datasets = []
    for jailbreak in jailbreaks:
        jailbroken_dataset = dataset.map(
            lambda x: {
                "jailbroken_prompt": convert_to_messages(
                    registered_jailbreaks[jailbreak](x["forbidden_prompt"], **kwargs)
                )
            },
            num_proc=multiprocessing.cpu_count(),
        )
        jailbroken_dataset = jailbroken_dataset.add_column(
            "jailbreak", len(jailbroken_dataset) * [jailbreak]
        )
        jailbroken_datasets.append(jailbroken_dataset)

    return concatenate_datasets(jailbroken_datasets)


def decode(response: str, jailbreak: str) -> str:
    """Decode a response.

    Args:
        response: Raw response.
        jailbreak: Jailbreak name.

    Returns:
        Decoded response.
    """
    decoder = registered_decoders.get(jailbreak, lambda x: x)
    return decoder(response)


def decode_dataset(dataset: Dataset) -> Dataset:
    """Decode a dataset containing raw responses.

    Args:
        dataset: Dataset with a "response" column containing the raw responses 
            and a "jailbreak" column with jailbreak names.

    Returns:
        Dataset with "response" column containing the decoded responses. 
        Raw responses are stored in a "raw_response" column.
    """
    dataset = dataset.map(
        lambda x: {"decoded_response": decode(x["response"], x["jailbreak"])},
        num_proc=multiprocessing.cpu_count(),
    )
    dataset = dataset.rename_column("response", "raw_response")
    dataset = dataset.rename_column("decoded_response", "response")
    return dataset
