import asyncio
import itertools
from typing import Awaitable, Callable, Iterable, List, TypeVar

T = TypeVar("T")
R = TypeVar("R")


async def process_in_batches(
    items: Iterable[T],
    handler: Callable[[List[T]], Awaitable[List[R]]],
    *,
    batch_size: int,
    concurrency: int,
) -> List[R]:
    """
    Splits items into batches and processes them concurrently using an async handler.

    This function takes an iterable of items, groups them into batches of a
    specified size, and calls an asynchronous handler for each batch. It ensures
    that no more than a specified number of handlers are running concurrently.
    The results from all batches are collected, flattened, and returned in the
    original order.

    Args:
        items: An iterable of items to be processed.
        handler: An asynchronous function that accepts a list of items (a batch)
                 and returns a list of results.
        batch_size: The size of each batch. Must be a positive integer.
        concurrency: The maximum number of concurrent handler calls. Must be a
                     positive integer.

    Returns:
        A flattened list of results from all batches, preserving the order
        of the original items.

    Raises:
        ValueError: If `batch_size` or `concurrency` is not a positive integer.
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if concurrency <= 0:
        raise ValueError("concurrency must be positive")

    semaphore = asyncio.Semaphore(concurrency)
    items_iterator = iter(items)
    tasks: List[asyncio.Task[List[R]]] = []

    async def worker(batch: List[T]) -> List[R]:
        async with semaphore:
            return await handler(batch)

    while True:
        batch = list(itertools.islice(items_iterator, batch_size))
        if not batch:
            break
        task = asyncio.create_task(worker(batch))
        tasks.append(task)

    if not tasks:
        return []

    results_by_batch: List[List[R]] = await asyncio.gather(*tasks)

    return [item for sublist in results_by_batch for item in sublist]
