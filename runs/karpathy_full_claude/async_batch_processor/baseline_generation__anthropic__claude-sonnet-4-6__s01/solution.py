"""
async_batch_processor.py

Provides process_in_batches: splits items into batches and runs an async handler
on each batch with bounded concurrency, returning flattened results in order.
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
    with at most *concurrency* concurrent handler calls, and return the
    flattened results in original batch order.

    Parameters
    ----------
    items       : sequence of items to process
    handler     : async callable that accepts a batch (list) and returns a list
    batch_size  : maximum number of items per batch (must be > 0)
    concurrency : maximum number of simultaneous handler invocations (must be > 0)

    Returns
    -------
    list of results, flattened in batch order
    """
    if batch_size <= 0:
        raise ValueError(f"batch_size must be a positive integer, got {batch_size!r}")
    if concurrency <= 0:
        raise ValueError(f"concurrency must be a positive integer, got {concurrency!r}")

    # Build batches, preserving order
    batches: List[List[Any]] = [
        list(items[i : i + batch_size]) for i in range(0, len(items), batch_size)
    ]

    if not batches:
        return []

    # Semaphore limits concurrent handler calls
    semaphore = asyncio.Semaphore(concurrency)

    async def run_batch(index: int, batch: List[Any]) -> tuple:
        async with semaphore:
            result = await handler(batch)
        return index, result

    # Schedule all batch tasks
    tasks = [asyncio.create_task(run_batch(i, batch)) for i, batch in enumerate(batches)]

    # Gather preserving exceptions; we want them to propagate naturally
    completed = await asyncio.gather(*tasks)

    # Sort by original index to guarantee order, then flatten
    completed_sorted = sorted(completed, key=lambda t: t[0])
    flattened: List[Any] = []
    for _, partial_results in completed_sorted:
        flattened.extend(partial_results)

    return flattened
