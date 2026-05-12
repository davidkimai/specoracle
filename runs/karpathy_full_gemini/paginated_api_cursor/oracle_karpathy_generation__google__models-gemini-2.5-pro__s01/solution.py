# paginated_api_cursor.py

"""A utility for collecting items from a cursor-paginated asynchronous API."""

from typing import Any, Awaitable, Callable, List, Optional, Tuple

# Type aliases for clarity. The specific types for Cursor and Item are
# determined by the API being called.
Cursor = Any
Item = Any
FetchPageResult = Tuple[List[Item], Optional[Cursor]]
FetchPageCallable = Callable[[Optional[Cursor]], Awaitable[FetchPageResult]]


async def collect_cursor_items(
    fetch_page: FetchPageCallable,
    *,
    start_cursor: Optional[Cursor] = None,
) -> List[Item]:
    """
    Collects items from a paginated API that uses a cursor.

    This function repeatedly calls an async `fetch_page` function, appending the
    items from each page to a result list. The process continues until the
    `fetch_page` function indicates there are no more pages by returning a
    `next_cursor` of `None`.

    Args:
        fetch_page: An async function that accepts a cursor and returns a tuple
            of (items, next_cursor). `items` is a list of items from the
            current page. `next_cursor` is the cursor for the next page, or
            `None` if it is the last page.
        start_cursor: The cursor to use for the first call to `fetch_page`.
            Defaults to `None`.

    Returns:
        A list containing all items collected from all pages, in the order
        they were received.
    """
    all_items: List[Item] = []
    current_cursor = start_cursor

    while True:
        items, next_cursor = await fetch_page(current_cursor)
        all_items.extend(items)

        if next_cursor is None:
            break

        current_cursor = next_cursor

    return all_items
