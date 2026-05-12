"""
A utility for collecting items from a cursor-paginated asynchronous API.
"""

from typing import Awaitable, Callable, List, Optional, Tuple, TypeVar

# Type variable for the items being collected.
T = TypeVar("T")
# Type variable for the cursor.
C = TypeVar("C")

FetchPageCallable = Callable[[Optional[C]], Awaitable[Tuple[List[T], Optional[C]]]]


async def collect_cursor_items(
    fetch_page: FetchPageCallable[T, C],
    *,
    start_cursor: Optional[C] = None,
) -> List[T]:
    """
    Collects items from a cursor-paginated asynchronous API.

    This function repeatedly calls an async `fetch_page` function, appending the
    items from each page to a result list. Pagination continues until the
    `fetch_page` function returns a `next_cursor` of `None`.

    Args:
        fetch_page: An async callable that accepts a cursor and returns a tuple
                    of (items, next_cursor). `items` is a list of items from
                    the current page, and `next_cursor` is the cursor for the
                    next page. If `next_cursor` is `None`, it signifies the
                    last page.
        start_cursor: The cursor to use for the first call to `fetch_page`.
                      Defaults to `None`.

    Returns:
        A single list containing all items collected from all pages in order.
    """
    all_items: List[T] = []
    current_cursor = start_cursor

    while True:
        items, next_cursor = await fetch_page(current_cursor)
        all_items.extend(items)

        if next_cursor is None:
            break

        current_cursor = next_cursor

    return all_items
