"""
paginated_api_cursor
====================
Async helper for collecting all items from a cursor-based paginated API.
"""


async def collect_cursor_items(fetch_page, *, start_cursor=None):
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
