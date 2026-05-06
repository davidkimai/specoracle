"""
paginated_api_cursor.py

Provides collect_cursor_items for consuming a cursor-based paginated async API.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine, List, Optional, Tuple


async def collect_cursor_items(
    fetch_page: Callable[
        [Optional[Any]],
        Coroutine[Any, Any, Tuple[List[Any], Optional[Any]]],
    ],
    *,
    start_cursor: Optional[Any] = None,
    per_page_timeout: Optional[float] = None,
) -> List[Any]:
    """
    Collect all items from a cursor-based paginated async source.

    Parameters
    ----------
    fetch_page:
        An async callable that accepts a cursor value and returns a tuple of
        (items, next_cursor).  When next_cursor is None the iteration stops.
    start_cursor:
        The cursor value passed to the very first call.  Defaults to None.
    per_page_timeout:
        Optional timeout in seconds applied to each individual page fetch via
        asyncio.wait_for.  When None (the default) no timeout is applied and
        the original behavior is preserved.

    Returns
    -------
    list
        A flat list of all items collected across every page.

    Raises
    ------
    asyncio.TimeoutError
        If per_page_timeout is set and a page fetch exceeds that duration.
    """
    all_items: List[Any] = []
    cursor: Optional[Any] = start_cursor

    while True:
        if per_page_timeout is None:
            items, next_cursor = await fetch_page(cursor)
        else:
            items, next_cursor = await asyncio.wait_for(
                fetch_page(cursor), timeout=per_page_timeout
            )
        all_items.extend(items)
        if next_cursor is None:
            break
        cursor = next_cursor

    return all_items
