from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable
from typing import Any, TypeVar

Item = TypeVar("Item")
Cursor = TypeVar("Cursor")


async def collect_cursor_items(
    fetch_page: Callable[[Cursor | None], Awaitable[tuple[Iterable[Item], Cursor | None]]],
    *,
    start_cursor: Cursor | None = None,
) -> list[Item]:
    """Collect all items from an async cursor-paginated API."""
    collected: list[Item] = []
    cursor: Cursor | None = start_cursor

    while True:
        items, next_cursor = await fetch_page(cursor)
        collected.extend(items)

        if next_cursor is None:
            return collected

        cursor = next_cursor


__all__ = ["collect_cursor_items"]
