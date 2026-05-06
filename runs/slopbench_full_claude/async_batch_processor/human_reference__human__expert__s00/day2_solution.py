from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from typing import Any


async def process_in_batches(
    items: Sequence[Any],
    handler: Callable[[list[Any]], Awaitable[list[Any]]],
    *,
    batch_size: int,
    concurrency: int,
    cancel_event: asyncio.Event | None = None,
) -> list[Any]:
    if batch_size <= 0 or concurrency <= 0:
        raise ValueError('batch_size and concurrency must be positive')

    batches = [list(items[index:index + batch_size]) for index in range(0, len(items), batch_size)]
    semaphore = asyncio.Semaphore(concurrency)

    async def run_batch(batch: list[Any]) -> list[Any]:
        async with semaphore:
            return await handler(batch)

    tasks: list[asyncio.Task[list[Any]]] = []
    for batch in batches:
        if cancel_event is not None and cancel_event.is_set():
            break
        tasks.append(asyncio.ensure_future(run_batch(batch)))

    results = await asyncio.gather(*tasks)
    return [item for batch_result in results for item in batch_result]
