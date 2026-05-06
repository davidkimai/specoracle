"""
paginated_api_cursor module

Provides collect_cursor_items for paginating through cursor-based async APIs.
"""

import asyncio


async def collect_cursor_items(fetch_page, *, start_cursor=None, per_page_timeout=None):
    """
    Collect all items from a cursor-based paginated async API.

    Parameters
    ----------
    fetch_page : async callable
        An async callable that accepts a cursor value and returns a tuple
        (items, next_cursor). When next_cursor is None, pagination stops.
    start_cursor : optional
        The cursor value to pass to the first call. Defaults to None.
    per_page_timeout : float or None, optional
        If set, each page fetch is wrapped with asyncio.wait_for using this
        value as the timeout in seconds. Raises asyncio.TimeoutError if a
        page fetch exceeds the timeout. Defaults to None (no timeout).

    Returns
    -------
    list
        All items collected across all pages.
    """
    all_items = []
    cursor = start_cursor

    while True:
        if per_page_timeout is not None:
            items, next_cursor = await asyncio.wait_for(
                fetch_page(cursor), timeout=per_page_timeout
            )
        else:
            items, next_cursor = await fetch_page(cursor)

        all_items.extend(items)
        if next_cursor is None:
            break
        cursor = next_cursor

    return all_items
