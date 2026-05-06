"""
priority_queue_merger.py

Merges multiple sorted iterables into a single sorted iterator lazily,
using a min-heap (priority queue) for efficient merging.
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
    # heap entries: (value, iterator_index, iterator)
    # iterator_index is used as a tiebreaker so that two equal values
    # never require comparing the iterator objects themselves.
    heap: list[tuple[int, int, Iterator[int]]] = []

    for idx, iterable in enumerate(iterators):
        it = iter(iterable)
        try:
            value = next(it)
            heapq.heappush(heap, (value, idx, it))
        except StopIteration:
            # Empty iterable — skip it
            pass

    while heap:
        value, idx, it = heapq.heappop(heap)
        yield value
        try:
            next_value = next(it)
            heapq.heappush(heap, (next_value, idx, it))
        except StopIteration:
            # This iterator is exhausted — don't re-push it
            pass
