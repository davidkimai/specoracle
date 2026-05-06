"""
priority_queue_merger.py

Merge multiple sorted iterables into a single sorted iterator using a min-heap.
"""

import heapq


def merge_sorted_iterators(iterators, source_weights=None):
    """Merge sorted input iterables lazily into a single sorted iterator.

    Parameters
    ----------
    iterators : list of iterable of int
        Each iterable must yield values in non-decreasing order.
    source_weights : list of int or None, optional
        When two values tie, the source with the lower weight wins.
        If omitted (or None), the lower source index is used as the
        tiebreaker (preserving original behaviour).

    Yields
    ------
    int
        Values from all iterables in sorted (non-decreasing) order.

    Raises
    ------
    TypeError
        If *iterators* is not iterable or contains non-iterable elements.
    ValueError
        If *source_weights* is provided but its length does not match
        the length of *iterators*.
    """
    if not isinstance(iterators, (list, tuple)):
        raise TypeError(f"Expected a list of iterables, got {type(iterators).__name__!r}")

    if source_weights is not None:
        if len(source_weights) != len(iterators):
            raise ValueError(
                f"source_weights length ({len(source_weights)}) must match "
                f"iterators length ({len(iterators)})"
            )
        weights = list(source_weights)
    else:
        # Default: use source index as weight so lower index wins on tie.
        weights = list(range(len(iterators)))

    heap = []

    for index, iterable in enumerate(iterators):
        it = iter(iterable)  # raises TypeError for non-iterables
        value = next(it, None)
        if value is not None:
            heapq.heappush(heap, (value, weights[index], index, it))

    while heap:
        value, weight, index, it = heapq.heappop(heap)
        yield value
        next_value = next(it, None)
        if next_value is not None:
            heapq.heappush(heap, (next_value, weights[index], index, it))
