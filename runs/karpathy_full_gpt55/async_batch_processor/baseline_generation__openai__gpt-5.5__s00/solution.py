import asyncio
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


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

    batches: list[list[T]] = []
    current_batch: list[T] = []

    for item in items:
        current_batch.append(item)
        if len(current_batch) == batch_size:
            batches.append(current_batch)
            current_batch = []

    if current_batch:
        batches.append(current_batch)

    if not batches:
        return []

    results: list[list[R] | None] = [None] * len(batches)
    next_batch_index = 0
    index_lock = asyncio.Lock()

    async def worker() -> None:
        nonlocal next_batch_index

        while True:
            async with index_lock:
                if next_batch_index >= len(batches):
                    return
                batch_index = next_batch_index
                next_batch_index += 1

            results[batch_index] = await handler(batches[batch_index])

    worker_count = min(concurrency, len(batches))

    async with asyncio.TaskGroup() as task_group:
        for _ in range(worker_count):
            task_group.create_task(worker())

    flattened: list[R] = []
    for batch_result in results:
        if batch_result is not None:
            flattened.extend(batch_result)

    return flattened
