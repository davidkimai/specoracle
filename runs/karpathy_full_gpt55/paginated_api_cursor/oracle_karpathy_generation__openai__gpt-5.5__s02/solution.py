from collections.abc import Awaitable, Callable, Iterable
from typing import Optional, TypeVar

T = TypeVar("T")
C = TypeVar("C")


async def collect_cursor_items(
    fetch_page: Callable[[Optional[C]], Awaitable[tuple[Iterable[T], Optional[C]]]],
    *,
    start_cursor: Optional[C] = None,
) -> list[T]:
    items: list[T] = []
    cursor = start_cursor

    while True:
        page_items, next_cursor = await fetch_page(cursor)
        items.extend(page_items)

        if next_cursor is None:
            return items

        cursor = next_cursor
