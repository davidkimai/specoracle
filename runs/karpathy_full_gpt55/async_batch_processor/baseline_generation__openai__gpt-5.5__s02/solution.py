import asyncio
from typing import Any, Awaitable, Callable, Iterable, List, TypeVar

T = TypeVar("T")
R = TypeVar("R")

__all__ = ["process_in_batches"]


def _validate_positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be a positive integer")
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _make_batches(items: Iterable[T], batch_size: int) -> List[List[T]]:
    batches: List[List[T]] = []
    batch: List[T] = []

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
    handler: Callable[[List[T]], Awaitable[List[R]]],
    *,
    batch_size: int,
    concurrency: int,
) -> List[R]:
    _validate_positive_int(batch_size, "batch_size")
    _validate_positive_int(concurrency, "concurrency")

    batches = _make_batches(items, batch_size)
    total_batches = len(batches)

    if total_batches == 0:
        return []

    results: List[Any] = [None] * total_batches
    next_index = 0

    async def worker() -> None:
        nonlocal next_index

        while True:
            index = next_index
            if index >= total_batches:
                return

            next_index = index + 1
            results[index] = await handler(batches[index])

    worker_count = min(concurrency, total_batches)
    tasks = [asyncio.create_task(worker()) for _ in range(worker_count)]

    try:
        await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise

    flattened: List[R] = []
    for batch_result in results:
        flattened.extend(batch_result)

    return flattened
