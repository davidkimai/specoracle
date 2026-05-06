"""
paginated_api_cursor
====================
Async helper for collecting all items from a cursor-based paginated API.
"""

import asyncio


async def collect_cursor_items(fetch_page, *, start_cursor=None, per_page_timeout=None):
    """Collect all items by following cursor pagination.

    Parameters
    ----------
    fetch_page:
        Async callable with signature ``async (cursor) -> (items, next_cursor)``.
        When *next_cursor* is ``None`` the caller signals that no further pages
        exist.
    start_cursor:
        Cursor value passed to the very first ``fetch_page`` call.
        Defaults to ``None``.
    per_page_timeout:
        Optional float. When set, each ``fetch_page`` call is wrapped in
        ``asyncio.wait_for`` with this timeout (in seconds). A
        ``asyncio.TimeoutError`` is raised if any single page fetch exceeds
        the limit. Defaults to ``None`` (no timeout).

    Returns
    -------
    list
        All items gathered across every page, in order.
    """
    if not callable(fetch_page):
        raise TypeError(f"fetch_page must be callable, got {type(fetch_page)!r}")

    all_items = []
    cursor = start_cursor

    while True:
        if per_page_timeout is not None:
            result = await asyncio.wait_for(fetch_page(cursor), timeout=per_page_timeout)
        else:
            result = await fetch_page(cursor)

        try:
            items, next_cursor = result
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "fetch_page must return a two-element sequence (items, next_cursor); "
                f"got {result!r}"
            ) from exc

        all_items.extend(items)

        if next_cursor is None:
            break

        cursor = next_cursor

    return all_items
