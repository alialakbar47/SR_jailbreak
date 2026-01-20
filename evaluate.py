"""
Evaluate Module - Unified Interface

This module provides a unified interface to all evaluators.
"""

# Re-export from evaluators module
from .evaluators import (
    registered_evaluators,
    register_evaluator,
    evaluate,
    evaluate_dataset,
)

__all__ = [
    "registered_evaluators",
    "register_evaluator",
    "evaluate",
    "evaluate_dataset",
]
