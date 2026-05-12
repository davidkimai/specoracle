"""
async_batch_processor.py

Provides process_in_batches: splits items into batches and runs an async
handler over them with bounded concurrency, returning flattened results
in original batch order.
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
    Split *items* into batches of *batch_size*, call *handler* on each batch
    with at most *concurrency* concurrent handler invocations, and return the
    flattened results in the original batch order.

    Parameters
    ----------
    items       : sequence of items to process
    handler     : async callable that receives one batch (list) and returns a list
    batch_size  : maximum number of items per batch (must be > 0)
    concurrency : maximum number of simultaneous handler calls (must be > 0)

    Returns
    -------
    list of results flattened in batch order
    """
    if batch_size <= 0:
        raise ValueError(f"batch_size must be positive, got {batch_size}")
    if concurrency <= 0:
        raise ValueError(f"concurrency must be positive, got {concurrency}")

    # Build ordered list of batches
    batches: List[List[Any]] = []
    for start in range(0, len(items), batch_size):
        batches.append(list(items[start : start + batch_size]))

    if not batches:
        return []

    # We need results indexed by batch position
    results: List[List[Any]] = [None] * len(batches)  # type: ignore[list-item]

    semaphore = asyncio.Semaphore(concurrency)

    async def run_batch(index: int, batch: List[Any]) -> None:
        async with semaphore:
            results[index] = await handler(batch)

    tasks = [
        asyncio.create_task(run_batch(i, batch))
        for i, batch in enumerate(batches)
    ]

    # Gather preserves task creation order; exceptions propagate here
    await asyncio.gather(*tasks)

    # Flatten in batch order
    flattened: List[Any] = []
    for batch_result in results:
        flattened.extend(batch_result)

    return flattened
