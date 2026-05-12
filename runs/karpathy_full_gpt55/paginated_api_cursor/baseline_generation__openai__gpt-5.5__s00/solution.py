from collections.abc import Awaitable, Callable, Iterable
from typing import Any, Optional, TypeVar

T = TypeVar("T")
Cursor = Any


async def collect_cursor_items(
    fetch_page: Callable[[Optional[Cursor]], Awaitable[tuple[Iterable[T], Optional[Cursor]]]],
    *,
    start_cursor: Optional[Cursor] = None,
) -> list[T]:
    """
    Collect items from an asynchronous cursor-paginated API.

    ``fetch_page`` is called with the current cursor and must return
    ``(items, next_cursor)``. Collection stops when ``next_cursor`` is None.
    """
    collected: list[T] = []
    cursor: Optional[Cursor] = start_cursor

    while True:
        items, next_cursor = await fetch_page(cursor)
        collected.extend(items)

        if next_cursor is None:
            break

        cursor = next_cursor

    return collected


__all__ = ["collect_cursor_items"]
