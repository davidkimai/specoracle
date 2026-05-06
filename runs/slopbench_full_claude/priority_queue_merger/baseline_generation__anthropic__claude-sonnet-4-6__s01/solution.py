"""
priority_queue_merger.py

Merges multiple sorted iterables into a single sorted iterator lazily,
using a min-heap (priority queue) for efficiency.
"""

import heapq


def merge_sorted_iterators(iterators):
    """
    Merge sorted input iterators lazily into a single sorted output iterator.

    Parameters
    ----------
    iterators : list of iterable of int
        A list of iterables, each yielding integers in non-decreasing order.

    Yields
    ------
    int
        Integers from all input iterables in non-decreasing (sorted) order.
    """
    heap = []

    # Initialize the heap with the first element from each iterator.
    # Heap entries are tuples (value, index, iterator) where index is used
    # as a tiebreaker to avoid comparing iterators directly.
    for index, iterable in enumerate(iterators):
        iterator = iter(iterable)
        try:
            value = next(iterator)
            heapq.heappush(heap, (value, index, iterator))
        except StopIteration:
            # Empty iterator; skip it.
            pass

    while heap:
        value, index, iterator = heapq.heappop(heap)
        yield value
        try:
            next_value = next(iterator)
            heapq.heappush(heap, (next_value, index, iterator))
        except StopIteration:
            # This iterator is exhausted; do not push it back.
            pass
