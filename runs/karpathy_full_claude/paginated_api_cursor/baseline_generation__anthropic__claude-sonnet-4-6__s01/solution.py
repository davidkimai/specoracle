"""
paginated_api_cursor.py

Provides collect_cursor_items for async cursor-based pagination.
"""

from typing import Any, Callable, Coroutine, List, Optional, Tuple


async def collect_cursor_items(
    fetch_page: Callable[
        [Optional[Any]],
        Coroutine[Any, Any, Tuple[List[Any], Optional[Any]]],
    ],
    *,
    start_cursor: Optional[Any] = None,
) -> List[Any]:
    """
    Collect all items from a cursor-paginated async API.

    Parameters
    ----------
    fetch_page:
        An async callable that accepts a cursor value and returns a tuple
        ``(items, next_cursor)``.  When ``next_cursor`` is ``None`` the
        iteration stops.
    start_cursor:
        The cursor value passed to the very first ``fetch_page`` call.
        Defaults to ``None``.

    Returns
    -------
    list
        All items collected across every page, in order.
    """
    all_items: List[Any] = []
    cursor: Optional[Any] = start_cursor

    while True:
        items, next_cursor = await fetch_page(cursor)
        all_items.extend(items)
        if next_cursor is None:
            break
        cursor = next_cursor

    return all_items
