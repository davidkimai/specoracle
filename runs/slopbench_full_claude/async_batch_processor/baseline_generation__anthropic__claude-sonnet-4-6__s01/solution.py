"""
async_batch_processor.py

Provides process_in_batches: splits items into batches and processes them
concurrently with a bounded concurrency limit, returning flattened results
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
    Split *items* into batches of *batch_size* and call *handler* on each batch,
    running at most *concurrency* handler calls concurrently.

    Parameters
    ----------
    items       : sequence of items to process
    handler     : async callable that accepts one batch (list) and returns a list
    batch_size  : maximum number of items per batch (must be > 0)
    concurrency : maximum number of simultaneous handler invocations (must be > 0)

    Returns
    -------
    Flattened list of results in the same order as the input batches.

    Raises
    ------
    ValueError  : if batch_size or concurrency is not positive
    """
    if batch_size <= 0:
        raise ValueError(f"batch_size must be positive, got {batch_size!r}")
    if concurrency <= 0:
        raise ValueError(f"concurrency must be positive, got {concurrency!r}")

    # Build ordered list of batches
    batches: List[List[Any]] = [
        items[i : i + batch_size] for i in range(0, len(items), batch_size)
    ]

    if not batches:
        return []

    # Pre-allocate result slots to maintain order
    results: List[Any] = [None] * len(batches)

    semaphore = asyncio.Semaphore(concurrency)

    async def process_one(index: int, batch: List[Any]) -> None:
        async with semaphore:
            results[index] = await handler(batch)

    tasks = [
        asyncio.create_task(process_one(idx, batch))
        for idx, batch in enumerate(batches)
    ]

    # Gather all tasks; propagate exceptions if any handler raises
    await asyncio.gather(*tasks)

    # Flatten results in batch order
    flattened: List[Any] = []
    for batch_result in results:
        if batch_result is not None:
            flattened.extend(batch_result)
        # If a batch legitimately returns an empty list, extend is a no-op, which
        # is correct.  None here would only occur if gather raised, so this branch
        # is safe.

    return flattened
