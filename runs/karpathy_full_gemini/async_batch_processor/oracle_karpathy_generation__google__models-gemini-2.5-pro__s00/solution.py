import asyncio
import itertools
from typing import Awaitable, Callable, Iterable, List, TypeVar

# Define generic type variables for input items and result items.
T = TypeVar('T')
R = TypeVar('R')


async def process_in_batches(
    items: Iterable[T],
    handler: Callable[[List[T]], Awaitable[List[R]]],
    *,
    batch_size: int,
    concurrency: int,
) -> List[R]:
    """
    Splits items into batches and processes them concurrently.

    Args:
        items: An iterable of items to process.
        handler: An async function that takes a batch (list of items) and
                 returns a list of results.
        batch_size: The maximum number of items in each batch.
        concurrency: The maximum number of concurrent handler calls.

    Returns:
        A flattened list of results from all batches, in the order of the
        original batches.

    Raises:
        ValueError: If batch_size or concurrency are not positive integers.
    """
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    if not isinstance(concurrency, int) or concurrency <= 0:
        raise ValueError("concurrency must be a positive integer")

    semaphore = asyncio.Semaphore(concurrency)
    tasks: List[asyncio.Task[List[R]]] = []

    async def worker(batch: List[T]) -> List[R]:
        """Acquires semaphore, calls handler, and releases semaphore."""
        async with semaphore:
            return await handler(batch)

    item_iterator = iter(items)
    while True:
        # Create a batch from the iterator using itertools.islice.
        batch = list(itertools.islice(item_iterator, batch_size))
        if not batch:
            # No more items to process.
            break

        task = asyncio.create_task(worker(batch))
        tasks.append(task)

    if not tasks:
        return []

    # Wait for all tasks to complete. The results will be in order.
    batch_results = await asyncio.gather(*tasks)

    # Flatten the list of lists into a single list of results.
    return [item for sublist in batch_results for item in sublist]
