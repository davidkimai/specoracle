from __future__ import annotations

import inspect
from collections.abc import Iterable
from typing import Any


__all__ = ["collect_cursor_items"]


async def collect_cursor_items(fetch_page: Any, *, start_cursor: Any = None) -> list[Any]:
    if not callable(fetch_page):
        raise TypeError("fetch_page must be an async callable")

    collected: list[Any] = []
    cursor = start_cursor

    while True:
        page = await _call_fetch_page(fetch_page, cursor)
        items, next_cursor = _unpack_page(page)

        collected.extend(_items_as_list(items))

        if next_cursor is None:
            return collected

        cursor = next_cursor


async def _call_fetch_page(fetch_page: Any, cursor: Any) -> Any:
    result = fetch_page(cursor)

    if not inspect.isawaitable(result):
        raise TypeError("fetch_page(cursor) must return an awaitable")

    return await result


def _unpack_page(page: Any) -> tuple[Any, Any]:
    if not isinstance(page, tuple) or len(page) != 2:
        raise TypeError("fetch_page(cursor) must resolve to a 2-tuple: (items, next_cursor)")

    return page


def _items_as_list(items: Any) -> list[Any]:
    if isinstance(items, (str, bytes, bytearray)):
        raise TypeError("page items must be an iterable of items, not a string-like object")

    if not isinstance(items, Iterable):
        raise TypeError("page items must be iterable")

    return list(items)
