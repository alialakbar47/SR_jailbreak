"""
StrongReject Adapted - Multi-Provider Jailbreak Evaluation Framework

This package provides a modernized and extended jailbreak evaluation framework 
with multi-provider API support (Google Gemini, OpenAI, Anthropic, HuggingFace).
"""

from .generate import generate, generate_to_dataset, convert_to_messages
from .jailbreaks import apply_jailbreaks, apply_jailbreaks_to_dataset, registered_jailbreaks
from .evaluate import evaluate, evaluate_dataset, registered_evaluators
from .load_datasets import load_strongreject_dataset

__version__ = "2.0.0"
__all__ = [
    "generate",
    "generate_to_dataset", 
    "convert_to_messages",
    "apply_jailbreaks",
    "apply_jailbreaks_to_dataset",
    "registered_jailbreaks",
    "evaluate",
    "evaluate_dataset",
    "registered_evaluators",
    "load_strongreject_dataset",
]
