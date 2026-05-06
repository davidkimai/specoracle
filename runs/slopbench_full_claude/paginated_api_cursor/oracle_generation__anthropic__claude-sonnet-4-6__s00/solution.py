"""
paginated_api_cursor
~~~~~~~~~~~~~~~~~~~~
Collect all items from a cursor-paginated async API.
"""


async def collect_cursor_items(fetch_page, *, start_cursor=None):
    """Exhaust a cursor-paginated source and return all items as a list.

    Parameters
    ----------
    fetch_page:
        An async callable with signature ``async (cursor) -> (items, next_cursor)``.
        *items* is an iterable of page results; *next_cursor* is the opaque
        cursor for the following page, or ``None`` when there are no more pages.
    start_cursor:
        Cursor passed to the very first ``fetch_page`` call (default ``None``).

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
