import asyncio
import itertools
from typing import Awaitable, Callable, Iterable, List, TypeVar

# Define generic type variables for input and output items.
T_in = TypeVar("T_in")
T_out = TypeVar("T_out")


async def process_in_batches(
    items: Iterable[T_in],
    handler: Callable[[List[T_in]], Awaitable[List[T_out]]],
    *,
    batch_size: int,
    concurrency: int,
) -> List[T_out]:
    """
    Splits items into batches and processes them concurrently using a handler.

    This function takes an iterable of items, groups them into batches, and
    runs an asynchronous handler on each batch. It controls the maximum
    number of concurrent handler executions.

    Args:
        items: An iterable of items to process.
        handler: An async callable that receives a list (a batch) of items
                 and returns a list of results for that batch.
        batch_size: The maximum number of items in a single batch.
        concurrency: The maximum number of handler calls to run concurrently.

    Returns:
        A single list containing the flattened results from all batches,
        preserving the order of the original batches.

    Raises:
        ValueError: If batch_size or concurrency are not positive integers.
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if concurrency <= 0:
        raise ValueError("concurrency must be positive")

    # A semaphore is used to limit the number of concurrent handler executions.
    semaphore = asyncio.Semaphore(concurrency)

    # This wrapper coroutine acquires the semaphore before calling the handler
    # and releases it afterwards, ensuring the concurrency limit is respected.
    async def process_one_batch(batch: List[T_in]) -> List[T_out]:
        """Acquires semaphore, calls handler, and returns results."""
        async with semaphore:
            return await handler(batch)

    # Create an iterator from the input to process it lazily.
    items_iterator = iter(items)
    tasks = []

    while True:
        # Lazily construct a batch from the iterator.
        batch = list(itertools.islice(items_iterator, batch_size))
        if not batch:
            # The iterator is exhausted, no more batches to create.
            break

        # Create a task for the batch. The task is scheduled on the event
        # loop but will be gated by the semaphore, respecting concurrency.
        task = asyncio.create_task(process_one_batch(batch))
        tasks.append(task)

    if not tasks:
        return []

    # asyncio.gather waits for all scheduled tasks to complete. Crucially,
    # it returns the results in the same order as the tasks were provided,
    # thus preserving the original batch order.
    results_from_batches = await asyncio.gather(*tasks)

    # Flatten the list of lists (results from each batch) into a single
    # list of results.
    flattened_results = [
        item for sublist in results_from_batches for item in sublist
    ]

    return flattened_results
