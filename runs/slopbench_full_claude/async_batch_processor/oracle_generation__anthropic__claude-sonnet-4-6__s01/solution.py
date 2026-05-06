"""
async_batch_processor.py

Provides process_in_batches: splits items into batches and runs an async
handler over them with bounded concurrency, returning flattened results in
original batch order.
"""

import asyncio
from typing import Any, Awaitable, Callable, List


def _make_batches(items: List[Any], batch_size: int) -> List[List[Any]]:
    """Partition items into consecutive chunks of at most batch_size."""
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]


async def _run_with_semaphore(
    semaphore: asyncio.Semaphore,
    index: int,
    batch: List[Any],
    handler: Callable[[List[Any]], Awaitable[List[Any]]],
) -> tuple[int, List[Any]]:
    """Acquire the semaphore, call handler, and return (index, result)."""
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
    Split items into batches of batch_size and run handler on each batch,
    allowing at most concurrency handlers to execute simultaneously.

    Parameters
    ----------
    items       : sequence of inputs to process
    handler     : async callable that receives one batch and returns a list
    batch_size  : maximum number of items per batch (must be > 0)
    concurrency : maximum number of concurrent handler invocations (must be > 0)

    Returns
    -------
    A flat list of results in the same order as the input batches.
    """
    if batch_size <= 0:
        raise ValueError(f"batch_size must be positive, got {batch_size!r}")
    if concurrency <= 0:
        raise ValueError(f"concurrency must be positive, got {concurrency!r}")

    batches = _make_batches(list(items), batch_size)

    if not batches:
        return []

    semaphore = asyncio.Semaphore(concurrency)

    tasks = [
        asyncio.create_task(_run_with_semaphore(semaphore, idx, batch, handler))
        for idx, batch in enumerate(batches)
    ]

    indexed_results = await asyncio.gather(*tasks)

    # Sort by original index to guarantee batch order, then flatten.
    ordered = [result for _, result in sorted(indexed_results, key=lambda t: t[0])]

    return [item for batch_result in ordered for item in batch_result]
