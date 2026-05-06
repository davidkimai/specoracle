"""
priority_queue_merger.py

Merge multiple sorted iterables into a single sorted iterator using a min-heap.
"""

import heapq


def merge_sorted_iterators(iterators):
    """Merge sorted input iterables lazily into a single sorted iterator.

    Parameters
    ----------
    iterators : list of iterable of int
        Each iterable must yield values in non-decreasing order.

    Yields
    ------
    int
        Values from all iterables in sorted (non-decreasing) order.

    Raises
    ------
    TypeError
        If *iterators* is not iterable or contains non-iterable elements.
    """
    if not isinstance(iterators, (list, tuple)):
        raise TypeError(f"Expected a list of iterables, got {type(iterators).__name__!r}")

    heap = []

    for index, iterable in enumerate(iterators):
        it = iter(iterable)  # raises TypeError for non-iterables
        value = next(it, None)
        if value is not None:
            heapq.heappush(heap, (value, index, it))

    while heap:
        value, index, it = heapq.heappop(heap)
        yield value
        next_value = next(it, None)
        if next_value is not None:
            heapq.heappush(heap, (next_value, index, it))
