"""
priority_queue_merger.py

Provides merge_sorted_iterators: merges multiple sorted iterables into a
single sorted iterator using a min-heap (priority queue).
"""

import heapq
from typing import Iterable, Iterator


def merge_sorted_iterators(iterators: list[Iterable[int]]) -> Iterator[int]:
    """
    Merge multiple sorted iterables lazily into a single sorted iterator.

    Parameters
    ----------
    iterators : list of sorted iterables of int
        Each iterable must yield integers in non-decreasing order.

    Yields
    ------
    int
        Integers in non-decreasing order drawn from all input iterables.
    """
    # Heap entries: (value, iterator_index, iterator)
    # iterator_index is used as a tiebreaker so that we never compare
    # two iterators directly (which would raise TypeError in Python 3).
    heap: list[tuple[int, int, Iterator[int]]] = []

    for idx, it in enumerate(iterators):
        it = iter(it)
        try:
            value = next(it)
            heapq.heappush(heap, (value, idx, it))
        except StopIteration:
            # Empty iterable – skip it.
            pass

    while heap:
        value, idx, it = heapq.heappop(heap)
        yield value
        try:
            next_value = next(it)
            heapq.heappush(heap, (next_value, idx, it))
        except StopIteration:
            # This iterator is exhausted; do not re-push it.
            pass
