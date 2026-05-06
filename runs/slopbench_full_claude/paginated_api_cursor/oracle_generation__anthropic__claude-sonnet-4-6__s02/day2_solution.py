"""
paginated_api_cursor
====================
Collect all items from a cursor-based paginated async API.
"""

import asyncio


async def collect_cursor_items(fetch_page, *, start_cursor=None, per_page_timeout=None):
    """Exhaust a cursor-paginated async source and return all items.

    Parameters
    ----------
    fetch_page:
        Async callable with signature ``async (cursor) -> (items, next_cursor)``.
        When *next_cursor* is ``None`` the sequence is complete.
    start_cursor:
        Cursor value passed to the very first ``fetch_page`` call.
        Defaults to ``None``.
    per_page_timeout:
        Optional float. When set, each ``fetch_page`` call is wrapped in
        ``asyncio.wait_for`` with this timeout (in seconds). When omitted or
        ``None``, no timeout is applied and original behavior is preserved.

    Returns
    -------
    list
        All items collected across every page, in order.

    Raises
    ------
    asyncio.TimeoutError
        If *per_page_timeout* is set and a page fetch exceeds the limit.
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
                "fetch_page must return a two-element sequence (items, next_cursor); "
                f"got {result!r}"
            ) from exc

        collected.extend(items)

        if next_cursor is None:
            return collected

        cursor = next_cursor
