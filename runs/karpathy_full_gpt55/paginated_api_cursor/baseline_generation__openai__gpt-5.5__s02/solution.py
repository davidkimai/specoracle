"""Utilities for collecting items from cursor-paginated async APIs."""

from collections.abc import Awaitable, Callable, Iterable
from typing import Optional, TypeVar

ItemT = TypeVar("ItemT")
CursorT = TypeVar("CursorT")

__all__ = ["collect_cursor_items"]


async def collect_cursor_items(
    fetch_page: Callable[
        [Optional[CursorT]],
        Awaitable[tuple[Iterable[ItemT], Optional[CursorT]]],
    ],
    *,
    start_cursor: Optional[CursorT] = None,
) -> list[ItemT]:
    """Collect all items from an async cursor-paginated fetch function."""
    cursor = start_cursor
    collected: list[ItemT] = []

    while True:
        items, next_cursor = await fetch_page(cursor)
        collected.extend(items)

        if next_cursor is None:
            return collected

        cursor = next_cursor
