"""
priority_queue_merger.py

Merges multiple sorted iterables into a single sorted iterator lazily,
using a min-heap (priority queue) for O(n log k) performance where n is
the total number of elements and k is the number of iterators.
"""

import heapq
from typing import Iterable, Iterator


def merge_sorted_iterators(iterators: list[Iterable[int]]) -> Iterator[int]:
    """
    Merge multiple sorted iterables into a single sorted iterator.

    Parameters
    ----------
    iterators : list of sorted iterables of int
        Each iterable must yield integers in non-decreasing order.

    Yields
    ------
    int
        Integers from all input iterables in non-decreasing order.
    """
    # heap entries: (value, tie_breaker_index, iterator)
    # tie_breaker_index ensures stable ordering when values are equal,
    # avoiding comparison of iterator objects (which may not support it).
    heap: list[tuple[int, int, Iterator[int]]] = []

    for index, iterable in enumerate(iterators):
        it = iter(iterable)
        try:
            value = next(it)
            heapq.heappush(heap, (value, index, it))
        except StopIteration:
            # Empty iterable – skip it
            pass

    while heap:
        value, index, it = heapq.heappop(heap)
        yield value
        try:
            next_value = next(it)
            heapq.heappush(heap, (next_value, index, it))
        except StopIteration:
            # This iterator is exhausted; do not re-add it
            pass
