"""
paginated_api_cursor.py

Provides collect_cursor_items: an async function that collects all items
from a cursor-based paginated API.
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
    Collect all items from a cursor-based paginated async API.

    Parameters
    ----------
    fetch_page : async callable
        An async callable that accepts a cursor (or None) and returns a
        tuple of (items, next_cursor).  When next_cursor is None the
        iteration stops.
    start_cursor : any, optional
        The cursor value to pass to the very first call.  Defaults to None.

    Returns
    -------
    list
        A flat list of every item returned across all pages.
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
