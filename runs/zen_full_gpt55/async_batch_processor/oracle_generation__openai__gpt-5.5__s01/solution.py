import asyncio
import inspect
from itertools import islice


def _require_positive_int(value, name):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _iter_batches(items, batch_size):
    try:
        iterator = iter(items)
    except TypeError as exc:
        raise TypeError("items must be iterable") from exc

    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            return
        yield batch


async def _run_batch(handler, batch, semaphore):
    async with semaphore:
        pending_result = handler(batch)
        if not inspect.isawaitable(pending_result):
            raise TypeError("handler must return an awaitable")

        result = await pending_result
        if not isinstance(result, list):
            raise TypeError("handler must return a list")

        return result


def _flatten(batch_results):
    flattened = []
    for batch_result in batch_results:
        flattened.extend(batch_result)
    return flattened


async def process_in_batches(items, handler, *, batch_size: int, concurrency: int) -> list:
    _require_positive_int(batch_size, "batch_size")
    _require_positive_int(concurrency, "concurrency")

    if not callable(handler):
        raise TypeError("handler must be callable")

    batches = list(_iter_batches(items, batch_size))
    if not batches:
        return []

    semaphore = asyncio.Semaphore(concurrency)
    tasks = [
        asyncio.create_task(_run_batch(handler, batch, semaphore))
        for batch in batches
    ]

    try:
        batch_results = await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise

    return _flatten(batch_results)


__all__ = ["process_in_batches"]
