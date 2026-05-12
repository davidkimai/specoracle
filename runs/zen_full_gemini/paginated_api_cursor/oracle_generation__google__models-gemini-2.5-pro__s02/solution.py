"""A module for collecting items from a paginated API using a cursor."""

from typing import Awaitable, Callable, List, Optional, Tuple, TypeVar

__all__ = ["collect_cursor_items"]

ItemType = TypeVar("ItemType")
CursorType = TypeVar("CursorType")


async def collect_cursor_items(
    fetch_page: Callable[
        [Optional[CursorType]],
        Awaitable[Tuple[List[ItemType], Optional[CursorType]]],
    ],
    *,
    start_cursor: Optional[CursorType] = None,
) -> List[ItemType]:
    """Collects all items from a cursor-paginated API.

    This function repeatedly calls an async `fetch_page` function, appending
    the items from each page to a result list until the API indicates there
    are no more pages.

    Args:
        fetch_page: An async callable that takes a cursor and returns a tuple
            of (items, next_cursor). `items` is a list of items for the
            current page. `next_cursor` is the cursor for the next page, or
            None if it is the last page. The callable must be able to handle
            `None` as a cursor value for the initial call.
        start_cursor: The initial cursor to start fetching from. Defaults to
            None.

    Returns:
        A list containing all items collected from all pages.

    Raises:
        Any exception raised by `fetch_page` will be propagated. This can
        include network errors, API-specific errors, or data parsing errors.
        Common propagated errors might include:
        - TypeError: If `fetch_page` is not an awaitable.
        - ValueError: If `fetch_page` does not return a 2-tuple that can be
          unpacked into (items, next_cursor).
    """
    all_items: List[ItemType] = []
    current_cursor = start_cursor

    while True:
        items, next_cursor = await fetch_page(current_cursor)
        all_items.extend(items)

        if next_cursor is None:
            break

        current_cursor = next_cursor

    return all_items
