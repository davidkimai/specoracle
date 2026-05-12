import asyncio
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


def _split_batches(items: Iterable[T], batch_size: int) -> list[list[T]]:
    batches: list[list[T]] = []
    batch: list[T] = []

    for item in items:
        batch.append(item)
        if len(batch) == batch_size:
            batches.append(batch)
            batch = []

    if batch:
        batches.append(batch)

    return batches


async def process_in_batches(
    items: Iterable[T],
    handler: Callable[[list[T]], Awaitable[list[R]]],
    *,
    batch_size: int,
    concurrency: int,
) -> list[R]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if concurrency <= 0:
        raise ValueError("concurrency must be positive")

    batches = _split_batches(items, batch_size)
    batch_results: list[list[R] | None] = [None] * len(batches)
    next_index = 0

    async def worker() -> None:
        nonlocal next_index

        while next_index < len(batches):
            index = next_index
            next_index += 1
            batch_results[index] = await handler(batches[index])

    workers = [
        asyncio.create_task(worker())
        for _ in range(min(concurrency, len(batches)))
    ]

    try:
        await asyncio.gather(*workers)
    except BaseException:
        for task in workers:
            task.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
        raise

    results: list[R] = []
    for batch_result in batch_results:
        if batch_result is not None:
            results.extend(batch_result)

    return results
