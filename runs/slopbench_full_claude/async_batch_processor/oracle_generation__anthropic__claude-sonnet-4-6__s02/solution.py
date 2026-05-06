"""
async_batch_processor.py

Provides process_in_batches: splits items into batches and runs an async
handler over them with bounded concurrency, returning flattened results
in original batch order.
"""

import asyncio
from typing import Any, Awaitable, Callable, List


def _make_batches(items: List[Any], batch_size: int) -> List[List[Any]]:
    """Slice items into consecutive chunks of at most batch_size."""
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]


async def _run_with_semaphore(
    semaphore: asyncio.Semaphore,
    index: int,
    batch: List[Any],
    handler: Callable[[List[Any]], Awaitable[List[Any]]],
) -> tuple:
    """Acquire semaphore, run handler, return (index, result) for ordering."""
    async with semaphore:
        result = await handler(batch)
    return index, result


async def process_in_batches(
    items: List[Any],
    handler: Callable[[List[Any]], Awaitable[List[Any]]],
    *,
    batch_size: int,
    concurrency: int,
) -> List[Any]:
    """
    Split items into batches of batch_size, run handler on each batch with
    at most concurrency handlers active simultaneously, and return a flat
    list of results in original batch order.

    Raises ValueError for non-positive batch_size or concurrency.
    """
    if batch_size <= 0:
        raise ValueError(f"batch_size must be positive, got {batch_size}")
    if concurrency <= 0:
        raise ValueError(f"concurrency must be positive, got {concurrency}")

    batches = _make_batches(list(items), batch_size)
    if not batches:
        return []

    semaphore = asyncio.Semaphore(concurrency)

    tasks = [
        asyncio.create_task(_run_with_semaphore(semaphore, idx, batch, handler))
        for idx, batch in enumerate(batches)
    ]

    indexed_results = await asyncio.gather(*tasks)

    # Sort by original batch index to guarantee order, then flatten.
    ordered = sorted(indexed_results, key=lambda pair: pair[0])
    return [item for _, batch_result in ordered for item in batch_result]
