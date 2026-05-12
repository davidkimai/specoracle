"""
A module for collecting items from a paginated API using a cursor-based strategy.
"""

from typing import (
    Awaitable,
    Callable,
    List,
    Optional,
    Tuple,
    TypeVar,
)

# Generic type for the items being collected.
ItemT = TypeVar("ItemT")
# Generic type for the cursor used for pagination.
CursorT = TypeVar("CursorT")

# Type alias for the fetch_page callable.
# It's an async function that takes an optional cursor and returns a tuple
# containing a list of items and the next cursor.
FetchPageCallable = Callable[
    [Optional[CursorT]],
    Awaitable[Tuple[List[ItemT], Optional[CursorT]]],
]


async def collect_cursor_items(
    fetch_page: FetchPageCallable[ItemT, CursorT],
    *,
    start_cursor: Optional[CursorT] = None,
) -> List[ItemT]:
    """
    Collects all items from a cursor-paginated asynchronous API.

    This function repeatedly calls the `fetch_page` function to get pages of
    items, appending them to a list until the API indicates there are no more
    pages.

    Args:
        fetch_page: An async callable that accepts a cursor and returns a
            tuple of (items, next_cursor). `items` is a list of items from
            the current page. `next_cursor` is the cursor for the subsequent
            page, or None if it's the last page.
        start_cursor: The initial cursor to use for the first call to
            `fetch_page`. Defaults to None.

    Returns:
        A list containing all items collected from all pages.
    """
    all_items: List[ItemT] = []
    current_cursor = start_cursor

    while True:
        items, next_cursor = await fetch_page(current_cursor)
        all_items.extend(items)

        if next_cursor is None:
            break
        current_cursor = next_cursor

    return all_items
