"""
priority_queue_merger
---------------------
Merge an arbitrary number of sorted iterables into a single sorted iterator.

Entry point: merge_sorted_iterators
"""

import heapq


def merge_sorted_iterators(iterators):
    """Merge sorted iterables lazily into a single sorted iterator.

    Parameters
    ----------
    iterators : list of iterable of int
        Each iterable must yield values in non-decreasing order.

    Yields
    ------
    int
        Values from all iterables in non-decreasing order.

    Raises
    ------
    TypeError
        If *iterators* is not iterable or any element is not iterable.
    """
    if not hasattr(iterators, '__iter__'):
        raise TypeError(f"Expected an iterable of iterables, got {type(iterators).__name__!r}")

    # heapq.merge handles the priority-queue logic internally and is lazy.
    wrapped = []
    for idx, it in enumerate(iterators):
        if not hasattr(it, '__iter__'):
            raise TypeError(
                f"Element at index {idx} is not iterable: {type(it).__name__!r}"
            )
        wrapped.append(iter(it))

    return heapq.merge(*wrapped)
