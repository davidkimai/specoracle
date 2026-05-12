import asyncio
import itertools
from typing import Awaitable, Callable, Iterable, List, TypeVar

T = TypeVar('T')
R = TypeVar('R')


def _generate_batches(items: Iterable[T], batch_size: int) -> Iterable[List[T]]:
    """
    Yields successive batches of a specified size from an iterable.

    This is a memory-efficient way to handle iterables of unknown length,
    as it does not require loading the entire sequence into memory at once.
    """
    iterator = iter(items)
    while True:
        # The list() constructor consumes from the islice iterator until the
        # batch is full or the iterator is exhausted.
        batch = list(itertools.islice(iterator, batch_size))
        if not batch:
            # When the iterator is exhausted, islice returns an empty sequence.
            break
        yield batch


async def _process_batch_with_semaphore(
    handler: Callable[[List[T]], Awaitable[List[R]]],
    batch: List[T],
    semaphore: asyncio.Semaphore,
) -> List[R]:
    """
    Awaits the semaphore, then calls the provided async handler with a batch.

    Using `async with` ensures the semaphore is released automatically, even
    if the handler raises an exception, preventing deadlocks.
    """
    async with semaphore:
        return await handler(batch)


async def process_in_batches(
    items: Iterable[T],
    handler: Callable[[List[T]], Awaitable[List[R]]],
    *,
    batch_size: int,
    concurrency: int,
) -> List[R]:
    """
    Splits items into batches and processes them concurrently.

    This function creates batches from the input items and runs the async
    handler on each batch, while limiting the number of concurrent handler
    executions to the specified concurrency level.

    Args:
        items: An iterable of items to process.
        handler: An async function that takes a list of items (a batch)
                 and returns a list of results.
        batch_size: The maximum number of items in each batch. Must be a
                    positive integer.
        concurrency: The maximum number of handler calls to run concurrently.
                     Must be a positive integer.

    Returns:
        A single list containing the flattened results from all batches,
        preserving the order of the batches.

    Raises:
        ValueError: If batch_size or concurrency are not positive integers.
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be a positive integer.")
    if concurrency <= 0:
        raise ValueError("concurrency must be a positive integer.")

    semaphore = asyncio.Semaphore(concurrency)

    tasks = [
        _process_batch_with_semaphore(handler, batch, semaphore)
        for batch in _generate_batches(items, batch_size)
    ]

    if not tasks:
        return []

    # asyncio.gather runs the awaitables concurrently and preserves the
    # order of the input sequence in the results. Since tasks were created
    # in batch order, the results will also be in batch order.
    batched_results: List[List[R]] = await asyncio.gather(*tasks)

    # Flatten the list of lists into a single list of results.
    return [item for sublist in batched_results for item in sublist]
