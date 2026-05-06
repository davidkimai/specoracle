"""
async_batch_processor.py

Provides process_in_batches: splits items into batches and runs an async
handler over each batch, respecting a concurrency limit, then returns
flattened results in original batch order.
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
    Split *items* into chunks of *batch_size* and call *handler* on each
    chunk, running at most *concurrency* handler calls concurrently.

    Parameters
    ----------
    items       : sequence of items to process
    handler     : async callable that receives a batch (list) and returns a list
    batch_size  : number of items per batch (must be > 0)
    concurrency : maximum number of concurrent handler invocations (must be > 0)

    Returns
    -------
    list
        Flattened results in the same order as the input batches.

    Raises
    ------
    ValueError
        If batch_size or concurrency is not a positive integer.
    """
    if batch_size <= 0:
        raise ValueError(f"batch_size must be a positive integer, got {batch_size!r}")
    if concurrency <= 0:
        raise ValueError(f"concurrency must be a positive integer, got {concurrency!r}")

    # Build ordered list of batches
    batches: List[List[Any]] = [
        list(items[i : i + batch_size]) for i in range(0, len(items), batch_size)
    ]

    if not batches:
        return []

    # We need results indexed by batch position, so we store (index, result) pairs.
    results: List[Any] = [None] * len(batches)

    semaphore = asyncio.Semaphore(concurrency)

    async def run_batch(index: int, batch: List[Any]) -> None:
        async with semaphore:
            result = await handler(batch)
            results[index] = result

    tasks = [
        asyncio.ensure_future(run_batch(idx, batch))
        for idx, batch in enumerate(batches)
    ]

    # Gather all tasks; propagate exceptions by default
    await asyncio.gather(*tasks)

    # Flatten results in batch order
    flattened: List[Any] = []
    for batch_result in results:
        if batch_result is not None:
            flattened.extend(batch_result)

    return flattened
