"""
paginated_api_cursor.py

Provides collect_cursor_items: an async function that paginates through
cursor-based API pages until exhausted.
"""


async def collect_cursor_items(fetch_page, *, start_cursor=None):
    """
    Collect all items from a cursor-based paginated async API.

    Parameters
    ----------
    fetch_page : async callable
        An async callable that accepts a cursor value and returns a tuple
        (items, next_cursor).  When next_cursor is None the sequence is
        exhausted.
    start_cursor : optional
        The cursor value to pass to the very first call.  Defaults to None.

    Returns
    -------
    list
        All items collected across every page, in order.
    """
    all_items = []
    cursor = start_cursor

    while True:
        items, next_cursor = await fetch_page(cursor)
        all_items.extend(items)
        if next_cursor is None:
            break
        cursor = next_cursor

    return all_items
