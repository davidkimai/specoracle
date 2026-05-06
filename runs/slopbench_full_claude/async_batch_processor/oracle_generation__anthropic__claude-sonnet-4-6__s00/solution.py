"""
async_batch_processor.py

Provides process_in_batches: splits items into batches and runs an async
handler over them with bounded concurrency, returning flattened results
in original batch order.
"""

import asyncio
from typing import Any, Awaitable, Callable, List


def _make_batches(items: List[Any], batch_size: int) -> List[List[Any]]:
    """Partition items into consecutive sublists of at most batch_size."""
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]


async def _run_with_semaphore(
    semaphore: asyncio.Semaphore,
    index: int,
    batch: List[Any],
    handler: Callable[[List[Any]], Awaitable[List[Any]]],
) -> tuple[int, List[Any]]:
    """Acquire the semaphore, call handler, return (index, results)."""
    async with semaphore:
        results = await handler(batch)
    return index, results


async def process_in_batches(
    items,
    handler: Callable[[List[Any]], Awaitable[List[Any]]],
    *,
    batch_size: int,
    concurrency: int,
) -> List[Any]:
    """
    Split items into batches of batch_size and process them with handler,
    running at most concurrency handlers concurrently.

    Parameters
    ----------
    items       : iterable of items to process
    handler     : async callable that accepts a batch (list) and returns a list
    batch_size  : maximum number of items per batch (must be positive)
    concurrency : maximum number of concurrent handler calls (must be positive)

    Returns
    -------
    Flattened list of results in the same order as the original batches.
    """
    if batch_size <= 0:
        raise ValueError(f"batch_size must be positive, got {batch_size!r}")
    if concurrency <= 0:
        raise ValueError(f"concurrency must be positive, got {concurrency!r}")

    all_items = list(items)
    if not all_items:
        return []

    batches = _make_batches(all_items, batch_size)
    semaphore = asyncio.Semaphore(concurrency)

    tasks = [
        asyncio.create_task(_run_with_semaphore(semaphore, idx, batch, handler))
        for idx, batch in enumerate(batches)
    ]

    indexed_results = await asyncio.gather(*tasks)

    # Sort by original batch index to guarantee order, then flatten.
    indexed_results_sorted = sorted(indexed_results, key=lambda pair: pair[0])
    flattened = [item for _, batch_result in indexed_results_sorted for item in batch_result]
    return flattened
