"""
async_batch_processor.py

Provides process_in_batches: splits items into batches and runs an async handler
with bounded concurrency, returning flattened results in original batch order.
"""

import asyncio
from typing import Any, Awaitable, Callable, List


async def process_in_batches(
    items: List[Any],
    handler: Callable[[List[Any]], Awaitable[List[Any]]],
    *,
    batch_size: int,
    concurrency: int,
) -> List[Any]:
    """
    Split *items* into batches of *batch_size*, invoke *handler* on each batch
    with at most *concurrency* concurrent calls, and return the flattened
    results in the original batch order.

    Parameters
    ----------
    items       : sequence of items to process
    handler     : async callable that accepts a batch (list) and returns a list
    batch_size  : maximum number of items per batch (must be > 0)
    concurrency : maximum number of simultaneous handler invocations (must be > 0)

    Returns
    -------
    list of results in the same order as the input batches, flattened one level.

    Raises
    ------
    ValueError  : if batch_size or concurrency is not a positive integer
    """
    if batch_size <= 0:
        raise ValueError(f"batch_size must be a positive integer, got {batch_size!r}")
    if concurrency <= 0:
        raise ValueError(f"concurrency must be a positive integer, got {concurrency!r}")

    # Build ordered list of batches
    batches: List[List[Any]] = []
    for start in range(0, len(items), batch_size):
        batches.append(list(items[start : start + batch_size]))

    if not batches:
        return []

    # Pre-allocate results list indexed by batch position
    results: List[Any] = [None] * len(batches)

    semaphore = asyncio.Semaphore(concurrency)

    async def run_batch(index: int, batch: List[Any]) -> None:
        async with semaphore:
            batch_result = await handler(batch)
            results[index] = batch_result

    # Schedule all tasks; the semaphore limits actual concurrency
    tasks = [
        asyncio.ensure_future(run_batch(i, batch))
        for i, batch in enumerate(batches)
    ]

    # Wait for all tasks, propagating the first exception if any
    done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    # Cancel any pending tasks (shouldn't be any with ALL_COMPLETED, but be safe)
    for task in pending:
        task.cancel()

    # Re-raise any exceptions from completed tasks
    for task in done:
        exc = task.exception()
        if exc is not None:
            raise exc

    # Flatten results in order
    flattened: List[Any] = []
    for batch_result in results:
        if batch_result is not None:
            flattened.extend(batch_result)

    return flattened
