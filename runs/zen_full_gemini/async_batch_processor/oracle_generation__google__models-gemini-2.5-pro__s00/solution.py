# -*- coding: utf-8 -*-
"""
An asynchronous utility for processing items in concurrent batches.
"""

import asyncio
from typing import Awaitable, Callable, Iterable, List, TypeVar

# Generic type variables for items and results to ensure type safety.
T_Item = TypeVar("T_Item")
T_Result = TypeVar("T_Result")

# A type alias for the asynchronous handler function provided by the user.
# The handler takes a list of items and returns a list of results.
Handler = Callable[[List[T_Item]], Awaitable[List[T_Result]]]


def _validate_positive_integer(value: object, name: str) -> None:
    """
    Raise ValueError if the provided value is not a positive integer.

    Args:
        value: The value to validate.
        name: The name of the parameter being validated, for the error message.

    Raises:
        ValueError: If value is not an integer or is not greater than zero.
    """
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer, but got {value!r}")


def _create_batches(
    items: Iterable[T_Item], batch_size: int
) -> Iterable[List[T_Item]]:
    """
    Yield successive batches of a specified size from an iterable.

    This is a generator function that processes the input iterable lazily,
    which is memory-efficient for large inputs.

    Args:
        items: An iterable of items to be batched.
        batch_size: The maximum number of items in each batch.

    Yields:
        A list of items representing a single batch. The final batch may be
        smaller than batch_size.
    """
    current_batch: List[T_Item] = []
    for item in items:
        current_batch.append(item)
        if len(current_batch) == batch_size:
            yield current_batch
            current_batch = []
    if current_batch:
        yield current_batch


async def _process_batch_with_semaphore(
    batch: List[T_Item],
    handler: Handler[T_Item, T_Result],
    semaphore: asyncio.Semaphore,
) -> List[T_Result]:
    """
    Acquire a semaphore, run the handler on a batch, and release the semaphore.

    This helper function encapsulates the concurrency control logic for processing
    a single batch.

    Args:
        batch: A list of items to process.
        handler: The async function to call with the batch.
        semaphore: The asyncio.Semaphore to control concurrency.

    Returns:
        The list of results returned by the handler for the given batch.
    """
    async with semaphore:
        return await handler(batch)


async def process_in_batches(
    items: Iterable[T_Item],
    handler: Handler[T_Item, T_Result],
    *,
    batch_size: int,
    concurrency: int,
) -> List[T_Result]:
    """
    Split items into batches and process them with a concurrent async handler.

    This function creates batches of `batch_size` from the input `items`, and
    runs the `handler` on up to `concurrency` batches simultaneously.

    Args:
        items: An iterable of items to be processed.
        handler: An async function that accepts a list of items (a batch) and
                 returns a list of results.
        batch_size: The maximum number of items in each batch. Must be a
                    positive integer.
        concurrency: The maximum number of handler calls to run concurrently.
                     Must be a positive integer.

    Returns:
        A single, flattened list containing the results from all batches,
        in the order that the batches were processed.

    Raises:
        ValueError: If `batch_size` or `concurrency` are not positive integers.
    """
    _validate_positive_integer(batch_size, "batch_size")
    _validate_positive_integer(concurrency, "concurrency")

    semaphore = asyncio.Semaphore(concurrency)
    tasks = []

    for batch in _create_batches(items, batch_size):
        task = asyncio.create_task(
            _process_batch_with_semaphore(batch, handler, semaphore)
        )
        tasks.append(task)

    if not tasks:
        return []

    # asyncio.gather preserves the order of the awaitables passed to it.
    # Since tasks were created in batch order, the results will be in order.
    results_from_all_batches = await asyncio.gather(*tasks)

    # Flatten the list of lists into a single list of results.
    return [
        item
        for batch_result in results_from_all_batches
        for item in batch_result
    ]
