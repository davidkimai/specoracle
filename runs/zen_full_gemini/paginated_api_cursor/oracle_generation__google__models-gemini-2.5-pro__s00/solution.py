"""
A module for collecting items from a paginated API using a cursor.
"""

import asyncio
from collections.abc import Iterable
from typing import (
    Awaitable,
    Callable,
    List,
    Optional,
    Tuple,
    TypeVar,
)

ItemT = TypeVar("ItemT")
CursorT = TypeVar("CursorT")

FetchPageCallable = Callable[
    [Optional[CursorT]],
    Awaitable[Tuple[List[ItemT], Optional[CursorT]]]
]

async def collect_cursor_items(
    fetch_page: FetchPageCallable[ItemT, CursorT],
    *,
    start_cursor: Optional[CursorT] = None,
) -> List[ItemT]:
    """
    Collects all items from a cursor-paginated asynchronous source.

    This function repeatedly calls an async `fetch_page` function, appending the
    items from each page to a result list. The pagination loop continues until
    `fetch_page` returns a `None` cursor, indicating the end of the data.

    Args:
        fetch_page: An async function that accepts a cursor and returns a
                    tuple of (items, next_cursor). `items` is a list of
                    results for the current page. `next_cursor` is the
                    cursor for the next page, or `None` if it is the last page.
        start_cursor: The initial cursor to use for the first call to
                      `fetch_page`. If `None`, the first call will receive
                      `None` as the cursor.

    Returns:
        A single list containing all items collected from all pages.

    Raises:
        TypeError: If `fetch_page` is not a coroutine function or if the
                   items returned are not an iterable.
        ValueError: If `fetch_page` does not return a tuple that can be
                    unpacked into two variables (items, next_cursor).
    """
    if not asyncio.iscoroutinefunction(fetch_page):
        raise TypeError("The `fetch_page` argument must be a coroutine function.")

    all_items: List[ItemT] = []
    current_cursor: Optional[CursorT] = start_cursor

    while True:
        try:
            items, next_cursor = await fetch_page(current_cursor)
        except (TypeError, ValueError) as e:
            raise ValueError(
                "The `fetch_page` function returned an invalid response. "
                "Expected a tuple of (items, next_cursor)."
            ) from e

        if not isinstance(items, Iterable):
            raise TypeError(
                f"The 'items' part of the `fetch_page` response must be an "
                f"iterable, but got {type(items).__name__}."
            )

        all_items.extend(items)

        if next_cursor is None:
            break

        current_cursor = next_cursor

    return all_items
