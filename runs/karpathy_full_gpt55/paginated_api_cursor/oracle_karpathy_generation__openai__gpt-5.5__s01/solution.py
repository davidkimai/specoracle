async def collect_cursor_items(fetch_page, *, start_cursor=None):
    """Collect items from an async cursor-paginated API."""
    collected = []
    cursor = start_cursor

    while True:
        items, next_cursor = await fetch_page(cursor)
        collected.extend(items)
        if next_cursor is None:
            return collected
        cursor = next_cursor
