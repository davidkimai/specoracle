async def collect_cursor_items(fetch_page, *, start_cursor=None):
    items = []
    cursor = start_cursor
    while True:
        page_items, next_cursor = await fetch_page(cursor)
        items.extend(page_items)
        if next_cursor is None:
            break
        cursor = next_cursor
    return items
