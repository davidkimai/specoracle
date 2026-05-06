"""
async_batch_processor.py

Provides process_in_batches: splits items into batches and runs an async
handler over each batch, respecting a concurrency limit, then returns
flattened results in original batch order.
"""

import asyncio
from typing import Any, Awaitable, Callable, List, Optional


async def process_in_batches(
    items: List[Any],
    handler: Callable[[List[Any]], Awaitable[List[Any]]],
    *,
    batch_size: int,
    concurrency: int,
    cancel_event: Optional[asyncio.Event] = None,
) -> List[Any]:
    """
    Split *items* into chunks of *batch_size* and call *handler* on each
    chunk, running at most *concurrency* handler calls concurrently.

    Parameters
    ----------
    items        : sequence of items to process
    handler      : async callable that receives a batch (list) and returns a list
    batch_size   : number of items per batch (must be > 0)
    concurrency  : maximum number of concurrent handler invocations (must be > 0)
    cancel_event : optional asyncio.Event; if set before a batch is scheduled,
                   no further batches will be started. Already-scheduled batches
                   run to completion and their results are included.

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

    # We need results indexed by batch position, so we store per-batch results.
    # Slots for batches that were never scheduled remain as the sentinel _UNSCHEDULED.
    _UNSCHEDULED = object()
    results: List[Any] = [_UNSCHEDULED] * len(batches)

    semaphore = asyncio.Semaphore(concurrency)

    async def run_batch(index: int, batch: List[Any]) -> None:
        async with semaphore:
            result = await handler(batch)
            results[index] = result

    tasks = []
    for idx, batch in enumerate(batches):
        # Check cancel_event before scheduling each new batch
        if cancel_event is not None and cancel_event.is_set():
            break
        tasks.append(asyncio.ensure_future(run_batch(idx, batch)))

    # Gather all scheduled tasks; propagate exceptions by default
    if tasks:
        await asyncio.gather(*tasks)

    # Flatten results in batch order, skipping unscheduled slots
    flattened: List[Any] = []
    for batch_result in results:
        if batch_result is _UNSCHEDULED:
            continue
        flattened.extend(batch_result)

    return flattened
