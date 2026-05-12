import inspect
from typing import Any


async def collect_cursor_items(fetch_page, *, start_cursor=None) -> list:
    if not callable(fetch_page):
        raise TypeError("fetch_page must be callable")

    cursor = start_cursor
    collected = []

    while True:
        page = await _fetch_page(fetch_page, cursor)
        items, next_cursor = _split_page(page)

        _extend_items(collected, items)

        if next_cursor is None:
            return collected

        cursor = next_cursor


async def _fetch_page(fetch_page, cursor: Any) -> Any:
    page_result = fetch_page(cursor)

    if not inspect.isawaitable(page_result):
        raise TypeError("fetch_page(cursor) must return an awaitable")

    return await page_result


def _split_page(page: Any) -> tuple[Any, Any]:
    if not isinstance(page, (tuple, list)):
        raise TypeError(
            "fetch_page(cursor) must resolve to a two-item tuple or list: "
            "(items, next_cursor)"
        )

    if len(page) != 2:
        raise ValueError(
            "fetch_page(cursor) must resolve to exactly two values: "
            "(items, next_cursor)"
        )

    return page[0], page[1]


def _extend_items(collected: list, items: Any) -> None:
    try:
        iterator = iter(items)
    except TypeError as exc:
        raise TypeError("page items must be iterable") from exc

    collected.extend(iterator)
