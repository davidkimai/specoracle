"""
An asynchronous, concurrent batch processing utility.

This module provides a function to process an iterable of items in batches,
with a specified level of concurrency for processing the batches themselves.
"""

import asyncio
import itertools
from typing import TypeVar, Callable, Iterable, List, Awaitable

# Type variables for generic type hinting, representing the input item type
# and the result item type.
T = TypeVar('T')
R = TypeVar('R')

# Type alias for the handler function. It's an async callable that accepts
# a list of items (a batch) and returns an awaitable that resolves to a
# list of results.
Handler = Callable[[List[T]], Awaitable[List[R]]]


async def process_in_batches(
    items: Iterable[T],
    handler: Handler[T, R],
    *,
    batch_size: int,
    concurrency: int,
) -> List[R]:
    """
    Splits items into batches and processes them concurrently.

    This function takes an iterable of items, groups them into batches of a
    specified size, and calls an asynchronous handler for each batch. It
    manages the concurrency of these handler calls, ensuring that no more than
    a specified number are running at any given time. The results from all
    batches are collected and returned as a single flattened list, preserving
    the order of the batches.

    Args:
        items: An iterable of items to process.
        handler: An async function (coroutine) that takes a list of items
                 (a batch) and returns a list of results.
        batch_size: The maximum number of items in each batch. Must be a
                    positive integer.
        concurrency: The maximum number of handler calls to run concurrently.
                     Must be a positive integer.

    Returns:
        A single list containing the flattened results from all batches,
        in the order the batches were created.

    Raises:
        ValueError: If `batch_size` or `concurrency` are not positive integers.
    """
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    if not isinstance(concurrency, int) or concurrency <= 0:
        raise ValueError("concurrency must be a positive integer")

    semaphore = asyncio.Semaphore(concurrency)
    tasks = []
    item_iterator = iter(items)

    async def process_one_batch(batch: List[T]) -> List[R]:
        """Acquire semaphore, call handler, and release semaphore."""
        async with semaphore:
            return await handler(batch)

    while True:
        # Create a batch from the iterator without pulling the entire
        # iterable into memory.
        batch = list(itertools.islice(item_iterator, batch_size))
        if not batch:
            break

        # Create a task for processing the batch. The task will start
        # running on the next event loop tick, but will wait for the
        # semaphore if concurrency limit is reached.
        task = asyncio.create_task(process_one_batch(batch))
        tasks.append(task)

    if not tasks:
        return []

    # asyncio.gather waits for all tasks to complete and returns their
    # results in the same order the tasks were provided.
    batch_results = await asyncio.gather(*tasks)

    # Flatten the list of lists (results from each batch) into a single list.
    return [item for sublist in batch_results for item in sublist]
