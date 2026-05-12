import asyncio
from itertools import islice
from numbers import Integral
from typing import Any, Awaitable, Callable, Iterable, List, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")


async def process_in_batches(
    items: Iterable[T],
    handler: Callable[[list[T]], Awaitable[Sequence[R]]],
    *,
    batch_size: int,
    concurrency: int,
) -> list[R]:
    if not isinstance(batch_size, Integral) or isinstance(batch_size, bool):
        raise TypeError("batch_size must be a positive integer")
    if not isinstance(concurrency, Integral) or isinstance(concurrency, bool):
        raise TypeError("concurrency must be a positive integer")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if concurrency <= 0:
        raise ValueError("concurrency must be positive")

    batches: list[list[T]] = []
    iterator = iter(items)
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            break
        batches.append(batch)

    if not batches:
        return []

    results_by_batch: list[Sequence[R] | None] = [None] * len(batches)
    next_index = 0
    index_lock = asyncio.Lock()

    async def worker() -> None:
        nonlocal next_index
        while True:
            async with index_lock:
                if next_index >= len(batches):
                    return
                batch_index = next_index
                next_index += 1

            results_by_batch[batch_index] = await handler(batches[batch_index])

    worker_count = min(concurrency, len(batches))
    tasks = [asyncio.create_task(worker()) for _ in range(worker_count)]

    try:
        await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise

    flattened: list[R] = []
    for batch_result in results_by_batch:
        if batch_result is not None:
            flattened.extend(batch_result)

    return flattened
