import asyncio
from typing import TypeVar, Callable, Awaitable, List, Iterable

T = TypeVar('T')
R = TypeVar('R')

AsyncBatchHandler = Callable[[List[T]], Awaitable[List[R]]]


async def process_in_batches(
    items: Iterable[T],
    handler: AsyncBatchHandler[T, R],
    *,
    batch_size: int,
    concurrency: int,
) -> List[R]:
    """
    Splits items into batches and processes them concurrently using a handler.

    This function chunks an iterable of items into smaller batches, and then
    runs an asynchronous handler function on each batch concurrently. The level
    of concurrency is controlled by the `concurrency` parameter.

    Args:
        items: An iterable of items to process.
        handler: An async function that accepts a batch (a list of items) and
                 returns a list of results for that batch.
        batch_size: The maximum number of items in each batch. Must be a
                    positive integer.
        concurrency: The maximum number of concurrent calls to the handler.
                     Must be a positive integer.

    Returns:
        A single, flattened list containing the results from all batches,
        preserved in the order of the original batches.

    Raises:
        ValueError: If `batch_size` or `concurrency` are not positive
                    integers.
    """
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    if not isinstance(concurrency, int) or concurrency <= 0:
        raise ValueError("concurrency must be a positive integer")

    def _generate_batches() -> Iterable[List[T]]:
        """Yields successive n-sized chunks from the items iterable."""
        batch = []
        for item in items:
            batch.append(item)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    semaphore = asyncio.Semaphore(concurrency)

    async def _process_batch_with_semaphore(batch: List[T]) -> List[R]:
        """Acquires semaphore, runs handler on batch, and releases."""
        async with semaphore:
            return await handler(batch)

    tasks = [
        asyncio.create_task(_process_batch_with_semaphore(batch))
        for batch in _generate_batches()
    ]

    if not tasks:
        return []

    # asyncio.gather preserves the order of the awaitables.
    results_from_batches: List[List[R]] = await asyncio.gather(*tasks)

    # Flatten the list of lists into a single list.
    return [item for sublist in results_from_batches for item in sublist]
