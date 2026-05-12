from __future__ import annotations

import heapq
from collections.abc import Iterable, Iterator


def merge_sorted_iterators(iterators: list[Iterable[int]]) -> Iterator[int]:
    """
    Lazily merge multiple sorted integer iterables into one sorted iterator.

    Each input iterable is assumed to yield integers in nondecreasing order.
    The function consumes only as much input as needed to produce each output
    value, keeping at most one pending value from each input iterable.
    """
    heap: list[tuple[int, int, Iterator[int]]] = []

    for index, iterable in enumerate(iterators):
        iterator = iter(iterable)
        try:
            first_value = next(iterator)
        except StopIteration:
            continue
        heapq.heappush(heap, (first_value, index, iterator))

    while heap:
        value, index, iterator = heapq.heappop(heap)
        yield value

        try:
            next_value = next(iterator)
        except StopIteration:
            continue

        heapq.heappush(heap, (next_value, index, iterator))
