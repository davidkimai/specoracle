"""
A module for collecting items from a cursor-paginated asynchronous API.
"""

from typing import (
    Awaitable,
    Callable,
    List,
    Optional,
    Tuple,
    TypeVar,
)

# Generic type variables for items and cursors to allow for static type checking
# by the caller.
TItem = TypeVar("TItem")
TCursor = TypeVar("TCursor")


async def collect_cursor_items(
    fetch_page: Callable[
        [Optional[TCursor]], Awaitable[Tuple[List[TItem], Optional[TCursor]]]
    ],
    *,
    start_cursor: Optional[TCursor] = None,
) -> List[TItem]:
    """
    Collects items from a cursor-paginated asynchronous source.

    This function repeatedly calls an async `fetch_page` function, appending the
    items from each page to a result list. The pagination process continues
    until `fetch_page` returns `None` as the next cursor.

    Args:
        fetch_page: An async callable that accepts a cursor and returns a tuple
                    of (items, next_cursor). `items` is a list of items from
                    the current page. `next_cursor` is the cursor for the next
                    page, or `None` if it is the last page.
        start_cursor: The initial cursor value to pass to the first call to
                      `fetch_page`. If not provided, `None` is used.

    Returns:
        A single list containing all items collected from all pages.
    """
    all_items: List[TItem] = []
    current_cursor = start_cursor

    while True:
        items, next_cursor = await fetch_page(current_cursor)
        all_items.extend(items)

        if next_cursor is None:
            break

        current_cursor = next_cursor

    return all_items
