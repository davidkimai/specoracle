"""
A module for collecting items from a paginated API that uses a cursor.
"""

from typing import (
    Any,
    Awaitable,
    Callable,
    List,
    Optional,
    Tuple,
    TypeVar,
)

T_Item = TypeVar("T_Item")
T_Cursor = TypeVar("T_Cursor")


async def collect_cursor_items(
    fetch_page: Callable[
        [Optional[T_Cursor]], Awaitable[Tuple[List[T_Item], Optional[T_Cursor]]]
    ],
    *,
    start_cursor: Optional[T_Cursor] = None,
) -> List[T_Item]:
    """
    Collects all items from a cursor-paginated asynchronous source.

    This function repeatedly calls an async `fetch_page` function, appending the
    items from each page to a result list. Pagination continues until
    `fetch_page` indicates there are no more pages by returning a `None`
    cursor.

    Args:
        fetch_page: An async callable that accepts a cursor and returns a
            tuple of (items, next_cursor). `items` is a list of items from
            the current page. `next_cursor` is the cursor for the next page,
            or `None` if it is the last page.
        start_cursor: The initial cursor to use for the first call to
            `fetch_page`. Defaults to `None`.

    Returns:
        A list containing all items collected from all pages.
    """
    all_items: List[T_Item] = []
    current_cursor: Optional[T_Cursor] = start_cursor

    while True:
        items, next_cursor = await fetch_page(current_cursor)
        all_items.extend(items)

        if next_cursor is None:
            break

        current_cursor = next_cursor

    return all_items
