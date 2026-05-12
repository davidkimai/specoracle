from collections.abc import Awaitable, Callable, Iterable
from typing import Any, TypeVar

T = TypeVar("T")


async def collect_cursor_items(
    fetch_page: Callable[[Any], Awaitable[tuple[Iterable[T], Any]]],
    *,
    start_cursor: Any = None,
) -> list[T]:
    cursor = start_cursor
    items: list[T] = []

    while True:
        page_items, next_cursor = await fetch_page(cursor)
        items.extend(page_items)
        if next_cursor is None:
            return items
        cursor = next_cursor
