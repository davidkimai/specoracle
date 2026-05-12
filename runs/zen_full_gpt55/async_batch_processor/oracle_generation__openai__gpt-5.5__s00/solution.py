from __future__ import annotations

import asyncio
import inspect
from collections.abc import Iterable
from typing import Any

__all__ = ["process_in_batches"]


def _validate_positive_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be a positive integer")
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _iterator_for(items: Iterable[Any]) -> Any:
    try:
        return iter(items)
    except TypeError as exc:
        raise TypeError("items must be an iterable") from exc


def _make_batches(items: Iterable[Any], batch_size: int) -> list[list[Any]]:
    batches: list[list[Any]] = []
    batch: list[Any] = []

    for item in _iterator_for(items):
        batch.append(item)
        if len(batch) == batch_size:
            batches.append(batch)
            batch = []

    if batch:
        batches.append(batch)

    return batches


async def _call_handler(handler: Any, batch: list[Any], semaphore: asyncio.Semaphore) -> list[Any]:
    async with semaphore:
        awaitable = handler(batch)
        if not inspect.isawaitable(awaitable):
            raise TypeError("handler must return an awaitable")

        result = await awaitable

    if not isinstance(result, list):
        raise TypeError("handler must return a list")

    return result


async def _gather_or_cancel(tasks: list[asyncio.Task[list[Any]]]) -> list[list[Any]]:
    try:
        return await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            if not task.done():
                task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
        raise


def _flatten(result_batches: Iterable[list[Any]]) -> list[Any]:
    flattened: list[Any] = []
    for result_batch in result_batches:
        flattened.extend(result_batch)
    return flattened


async def process_in_batches(
    items: Iterable[Any],
    handler: Any,
    *,
    batch_size: int,
    concurrency: int,
) -> list[Any]:
    _validate_positive_int("batch_size", batch_size)
    _validate_positive_int("concurrency", concurrency)

    if not callable(handler):
        raise TypeError("handler must be callable")

    batches = _make_batches(items, batch_size)
    if not batches:
        return []

    semaphore = asyncio.Semaphore(concurrency)
    tasks = [
        asyncio.create_task(_call_handler(handler, batch, semaphore))
        for batch in batches
    ]

    result_batches = await _gather_or_cancel(tasks)
    return _flatten(result_batches)
