from typing import Awaitable, Callable, List, Optional, Tuple, TypeVar

T = TypeVar("T")
C = TypeVar("C")

FetchPage = Callable[[Optional[C]], Awaitable[Tuple[List[T], Optional[C]]]]


async def collect_cursor_items(
    fetch_page: FetchPage[T, C],
    *,
    start_cursor: Optional[C] = None,
) -> List[T]:
    """Collects items from a paginated API using a cursor.

    This function repeatedly calls an async `fetch_page` callable, appending the
    items from each page to a result list. Pagination continues until the
    `fetch_page` callable returns `None` as the next cursor.

    Args:
        fetch_page: An async callable that takes a cursor and returns a tuple
                    of (items, next_cursor). `items` is a list of items from
                    the current page. `next_cursor` is the cursor for the next
                    page, or `None` if it is the last page.
        start_cursor: The initial cursor to use for the first call to
                      `fetch_page`. Defaults to `None`.

    Returns:
        A list containing all items collected from all pages.

    Raises:
        TypeError: If the `items` component returned by `fetch_page` is not a
                   list. Any exception raised by `fetch_page` will be
                   propagated.
    """
    all_items: List[T] = []
    current_cursor = start_cursor

    while True:
        page_items, next_cursor = await fetch_page(current_cursor)

        if not isinstance(page_items, list):
            raise TypeError(
                f"The 'items' returned by fetch_page must be a list, "
                f"but got {type(page_items).__name__}."
            )

        all_items.extend(page_items)

        if next_cursor is None:
            break

        current_cursor = next_cursor

    return all_items
