"""
Evaluator Registry Module

Provides registration and management of evaluators.
"""

import multiprocessing
from typing import Callable, Dict, List
from datasets import Dataset, concatenate_datasets

# Global registry
registered_evaluators: Dict[str, tuple] = {}


def register_evaluator(key: str, parallelism: str = "multiprocessing") -> Callable:
    """Register a new evaluator.

    Args:
        key: Evaluator name.
        parallelism: Type of parallelism ("batched" or "multiprocessing").

    Returns:
        Decorator function.
    """
    valid_parallelisms = ("multiprocessing", "batched")
    if parallelism not in valid_parallelisms:
        raise ValueError(f"parallelism must be one of {valid_parallelisms}. Got {parallelism}.")

    def inner(func):
        registered_evaluators[key] = (func, parallelism)
        return func

    return inner


def evaluate(
    forbidden_prompt: str, 
    response: str, 
    evaluators: List[str], 
    **kwargs
) -> List[Dict[str, float]]:
    """Evaluate a single forbidden prompt-response pair.

    Args:
        forbidden_prompt: Forbidden prompt.
        response: Response.
        evaluators: List of evaluators to run.
        **kwargs: Additional arguments passed to evaluators.

    Returns:
        List of dictionaries mapping "score" to harmfulness scores between 0 and 1.
    """
    results = []
    for evaluator in evaluators:
        func, parallelism = registered_evaluators[evaluator]
        if parallelism == "multiprocessing":
            result = func(forbidden_prompt, response, **kwargs)
        else:
            result = func(
                {"forbidden_prompt": [forbidden_prompt], "response": [response]}, **kwargs
            )
            for key, value in result.items():
                if isinstance(value, list) and len(value) == 1:
                    result[key] = value[0]

        results.append(result)

    return results


def evaluate_dataset(
    dataset: Dataset,
    evaluators: List[str],
    batch_size: int = 1,
    **kwargs,
) -> Dataset:
    """Evaluate a dataset of forbidden prompt-response pairs.

    Args:
        dataset: Dataset to evaluate.
        evaluators: List of evaluators.
        batch_size: Batch size for evaluators that support batched processing.
        **kwargs: Additional arguments passed to evaluators.

    Returns:
        Dataset with evaluation scores.
    """
    evaluated_datasets = []
    for evaluator in evaluators:
        func, parallelism = registered_evaluators[evaluator]
        if parallelism == "multiprocessing":
            if "answer" in dataset.features:
                evaluated_dataset = dataset.map(
                    lambda x: func(
                        x["forbidden_prompt"], x["response"], answer=x["answer"], **kwargs
                    ),
                    num_proc=multiprocessing.cpu_count(),
                )
            else:
                evaluated_dataset = dataset.map(
                    lambda x: func(x["forbidden_prompt"], x["response"], **kwargs),
                    num_proc=multiprocessing.cpu_count(),
                )
        else:
            evaluated_dataset = dataset.map(
                lambda x: func(x, **kwargs), batched=True, batch_size=batch_size
            )

        evaluated_dataset = evaluated_dataset.add_column(
            "evaluator", len(evaluated_dataset) * [evaluator]
        )
        evaluated_datasets.append(evaluated_dataset)

    return concatenate_datasets(evaluated_datasets)
