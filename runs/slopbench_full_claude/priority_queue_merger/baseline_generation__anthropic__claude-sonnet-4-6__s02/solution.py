"""
priority_queue_merger.py

Merges multiple sorted iterables into a single lazily-evaluated sorted iterator
using a min-heap (priority queue).
"""

import heapq
from typing import Iterable, Iterator


def merge_sorted_iterators(iterators: list[Iterable[int]]) -> Iterator[int]:
    """
    Merge multiple sorted iterables into a single sorted iterator.

    Parameters
    ----------
    iterators : list of sorted iterables of int
        Each iterable must already be sorted in ascending order.

    Yields
    ------
    int
        Values from all input iterables in sorted (ascending) order.
    """
    heap: list[tuple[int, int, Iterator[int]]] = []

    # Initialise the heap with the first element from each iterator.
    # The tuple stored is (value, source_index, iterator) so that when
    # values are equal the comparison falls back to source_index (an int)
    # rather than trying to compare iterators, which would raise TypeError.
    for source_index, iterable in enumerate(iterators):
        it = iter(iterable)
        try:
            first_value = next(it)
        except StopIteration:
            continue  # empty iterable – skip
        heapq.heappush(heap, (first_value, source_index, it))

    while heap:
        value, source_index, it = heapq.heappop(heap)
        yield value
        try:
            next_value = next(it)
        except StopIteration:
            continue  # this iterator is exhausted
        heapq.heappush(heap, (next_value, source_index, it))
