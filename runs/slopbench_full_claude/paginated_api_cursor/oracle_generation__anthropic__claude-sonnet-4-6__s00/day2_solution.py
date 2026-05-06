"""
paginated_api_cursor
~~~~~~~~~~~~~~~~~~~~
Collect all items from a cursor-paginated async API.
"""

import asyncio


async def collect_cursor_items(fetch_page, *, start_cursor=None, per_page_timeout=None):
    """Exhaust a cursor-paginated source and return all items as a list.

    Parameters
    ----------
    fetch_page:
        An async callable with signature ``async (cursor) -> (items, next_cursor)``.
        *items* is an iterable of page results; *next_cursor* is the opaque
        cursor for the following page, or ``None`` when there are no more pages.
    start_cursor:
        Cursor passed to the very first ``fetch_page`` call (default ``None``).
    per_page_timeout:
        Optional float. When set, each ``fetch_page`` call is wrapped in
        ``asyncio.wait_for`` with this timeout (in seconds). A
        ``asyncio.TimeoutError`` is raised if any single page fetch exceeds
        the limit. When ``None`` (default), no timeout is applied.

    Returns
    -------
    list
        All items collected across every page, in order.
    """
    if not callable(fetch_page):
        raise TypeError(f"fetch_page must be callable, got {type(fetch_page)!r}")

    collected = []
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
                "fetch_page must return a two-element sequence (items, next_cursor)"
            ) from exc

        collected.extend(items)

        if next_cursor is None:
            return collected

        cursor = next_cursor
