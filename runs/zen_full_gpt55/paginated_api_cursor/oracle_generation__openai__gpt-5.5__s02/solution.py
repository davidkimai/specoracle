from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Iterable
from typing import Any, TypeAlias, TypeVar

Item = TypeVar("Item")
Cursor: TypeAlias = Any
Page: TypeAlias = tuple[Iterable[Item], Cursor | None]


async def collect_cursor_items(
    fetch_page: Callable[[Cursor | None], Awaitable[Page[Item]]],
    *,
    start_cursor: Cursor | None = None,
) -> list[Item]:
    if not callable(fetch_page):
        raise TypeError("fetch_page must be callable")

    collected: list[Item] = []
    cursor = start_cursor

    while True:
        page = await _fetch_page(fetch_page, cursor)
        page_items, next_cursor = _validate_page(page)

        collected.extend(page_items)

        if next_cursor is None:
            return collected

        cursor = next_cursor


async def _fetch_page(
    fetch_page: Callable[[Cursor | None], Awaitable[object]],
    cursor: Cursor | None,
) -> object:
    page_awaitable = fetch_page(cursor)

    if not inspect.isawaitable(page_awaitable):
        raise TypeError("fetch_page(cursor) must return an awaitable")

    return await page_awaitable


def _validate_page(page: object) -> Page[Any]:
    if not isinstance(page, tuple):
        raise TypeError("fetch_page must resolve to a tuple: (items, next_cursor)")

    if len(page) != 2:
        raise ValueError("fetch_page result must contain exactly two values")

    page_items, next_cursor = page

    if not isinstance(page_items, Iterable):
        raise TypeError("page items must be iterable")

    return page_items, next_cursor
