# -*- coding: utf-8 -*-
"""
An asynchronous batch processor for concurrently handling items.
"""

import asyncio
import itertools
from typing import Awaitable, Callable, Iterable, List, TypeVar

# Generic type variables for item and result types, allowing for flexible
# type hinting of the items being processed and the results being returned.
T = TypeVar('T')
R = TypeVar('R')


async def _worker(
    handler: Callable[[List[T]], Awaitable[List[R]]],
    batch: List[T],
    semaphore: asyncio.Semaphore
) -> List[R]:
    """
    A coroutine that acquires a semaphore, runs the handler on a batch,
    and ensures the semaphore is released.
    """
    async with semaphore:
        # The handler might raise an exception. The semaphore is released
        # automatically by 'async with', and asyncio.gather will propagate
        # the exception from the failed task.
        return await handler(batch)


def _generate_batches(
    items: Iterable[T],
    batch_size: int
) -> Iterable[List[T]]:
    """
    Yields successive, non-overlapping chunks of a specific size from an
    iterable. This implementation is memory-efficient as it does not load
    the entire iterable into memory.
    """
    it = iter(items)
    while True:
        # itertools.islice is an efficient way to get the next N items
        # from an iterator.
        batch = list(itertools.islice(it, batch_size))
        if not batch:
            # The iterator is exhausted when an empty batch is returned.
            return
        yield batch


async def process_in_batches(
    items: Iterable[T],
    handler: Callable[[List[T]], Awaitable[List[R]]],
    *,
    batch_size: int,
    concurrency: int
) -> List[R]:
    """
    Splits items into batches and processes them concurrently.

    This function takes an iterable of items, groups them into batches of a
    specified size, and runs an asynchronous handler on each batch. It limits
    the number of concurrently running handlers to the specified concurrency
    level.

    Args:
        items: An iterable of items to process.
        handler: An async function that receives a list of items (a batch)
                 and returns a list of results. The results from the handler
                 should correspond to the items in the batch.
        batch_size: The maximum number of items in each batch. Must be a
                    positive integer.
        concurrency: The maximum number of concurrent handler calls. Must be a
                     positive integer.

    Returns:
        A single list containing the flattened results from all batches,
        with the order preserved relative to the input `items` iterable.

    Raises:
        ValueError: If `batch_size` or `concurrency` are not positive integers.
    """
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")

    if not isinstance(concurrency, int) or concurrency <= 0:
        raise ValueError("concurrency must be a positive integer")

    semaphore = asyncio.Semaphore(concurrency)
    tasks = []

    for batch in _generate_batches(items, batch_size):
        # For each batch, create a task that will run the handler.
        # The _worker helper ensures that the semaphore is acquired before
        # the handler is called.
        task = asyncio.create_task(
            _worker(handler, batch, semaphore)
        )
        tasks.append(task)

    if not tasks:
        return []

    # await asyncio.gather to run all tasks concurrently and collect results.
    # The order of results from gather corresponds to the order of tasks
    # (and thus the order of the original batches).
    results_from_all_batches = await asyncio.gather(*tasks)

    # Flatten the list of lists into a single list of results.
    return [item for sublist in results_from_all_batches for item in sublist]
