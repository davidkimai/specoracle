from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


async def collect_cursor_items(
    fetch_page: Callable[[Any], Awaitable[tuple[list[Any], Any]]],
    *,
    start_cursor: Any = None,
    per_page_timeout: float | None = None,
) -> list[Any]:
    cursor = start_cursor
    collected: list[Any] = []
    while True:
        if per_page_timeout is None:
            items, cursor = await fetch_page(cursor)
        else:
            items, cursor = await asyncio.wait_for(
                fetch_page(cursor), timeout=per_page_timeout
            )
        collected.extend(items)
        if cursor is None:
            return collected
