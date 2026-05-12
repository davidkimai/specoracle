"""A module for collecting items from a cursor-paginated asynchronous source."""

from typing import (
    Awaitable,
    Callable,
    List,
    Optional,
    Tuple,
    TypeVar,
)

_ItemT = TypeVar("_ItemT")
_CursorT = TypeVar("_CursorT")


async def collect_cursor_items(
    fetch_page: Callable[
        [Optional[_CursorT]], Awaitable[Tuple[List[_ItemT], Optional[_CursorT]]]
    ],
    *,
    start_cursor: Optional[_CursorT] = None,
) -> List[_ItemT]:
    """
    Collects items from a cursor-paginated asynchronous source.

    This function repeatedly calls an async `fetch_page` function, appending the
    items from each page to a list. Pagination continues until `fetch_page`
    returns a `next_cursor` of `None`.

    Args:
        fetch_page: An async callable that accepts a cursor and returns a
            tuple of (items, next_cursor). `items` is a list of items from
            the current page. `next_cursor` is the cursor for the next page,
            or `None` if it's the last page.
        start_cursor: The initial cursor to use for the first call to
            `fetch_page`. Defaults to `None`.

    Returns:
        A list containing all items collected from all pages.
    """
    all_items: List[_ItemT] = []
    current_cursor = start_cursor

    while True:
        items, next_cursor = await fetch_page(current_cursor)
        all_items.extend(items)

        if next_cursor is None:
            break

        current_cursor = next_cursor

    return all_items
