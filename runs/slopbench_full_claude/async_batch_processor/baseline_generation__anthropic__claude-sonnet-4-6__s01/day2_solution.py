"""
async_batch_processor.py

Provides process_in_batches: splits items into batches and processes them
concurrently with a bounded concurrency limit, returning flattened results
in original batch order.
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
    Split *items* into batches of *batch_size* and call *handler* on each batch,
    running at most *concurrency* handler calls concurrently.

    Parameters
    ----------
    items        : sequence of items to process
    handler      : async callable that accepts one batch (list) and returns a list
    batch_size   : maximum number of items per batch (must be > 0)
    concurrency  : maximum number of simultaneous handler invocations (must be > 0)
    cancel_event : optional asyncio.Event; if set before a batch is scheduled,
                   no further batches will be started.  Results from already
                   scheduled (or completed) batches are still returned in order.

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

    # Pre-allocate result slots to maintain order; sentinel distinguishes
    # "not scheduled / cancelled" from a legitimate empty-list result.
    _UNSET = object()
    results: List[Any] = [_UNSET] * len(batches)

    semaphore = asyncio.Semaphore(concurrency)

    async def process_one(index: int, batch: List[Any]) -> None:
        async with semaphore:
            results[index] = await handler(batch)

    tasks = []
    for idx, batch in enumerate(batches):
        # Check cancel_event before scheduling each new batch
        if cancel_event is not None and cancel_event.is_set():
            break
        tasks.append(asyncio.create_task(process_one(idx, batch)))

    # Gather all scheduled tasks; propagate exceptions if any handler raises
    if tasks:
        await asyncio.gather(*tasks)

    # Flatten results in batch order, skipping unscheduled (cancelled) slots
    flattened: List[Any] = []
    for batch_result in results:
        if batch_result is _UNSET:
            # This batch was never scheduled due to cancellation; stop here
            # to preserve order integrity (no gaps).
            break
        flattened.extend(batch_result)

    return flattened
