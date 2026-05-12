async def collect_cursor_items(fetch_page, *, start_cursor=None):
    results = []
    cursor = start_cursor
    while True:
        items, next_cursor = await fetch_page(cursor)
        results.extend(items)
        if next_cursor is None:
            break
        cursor = next_cursor
    return results
