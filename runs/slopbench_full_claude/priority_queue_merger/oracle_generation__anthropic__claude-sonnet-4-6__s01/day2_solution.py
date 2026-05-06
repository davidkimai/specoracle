"""
priority_queue_merger
---------------------
Merge an arbitrary number of sorted iterables into a single sorted iterator.

Entry point: merge_sorted_iterators
"""

import heapq


def merge_sorted_iterators(iterators, source_weights=None):
    """Merge sorted iterables lazily into a single sorted iterator.

    Parameters
    ----------
    iterators : list of iterable of int
        Each iterable must yield values in non-decreasing order.
    source_weights : list of int or None, optional
        When two values are equal the source with the lower weight is yielded
        first.  If omitted (or None) the source index acts as the weight, so
        lower-indexed sources win ties.  Must have the same length as
        *iterators* when provided.

    Yields
    ------
    int
        Values from all iterables in non-decreasing order.

    Raises
    ------
    TypeError
        If *iterators* is not iterable or any element is not iterable.
    ValueError
        If *source_weights* is provided but its length differs from
        *iterators*.
    """
    if not hasattr(iterators, '__iter__'):
        raise TypeError(
            f"Expected an iterable of iterables, got {type(iterators).__name__!r}"
        )

    # Materialise so we can index and validate once.
    iterators = list(iterators)

    for idx, it in enumerate(iterators):
        if not hasattr(it, '__iter__'):
            raise TypeError(
                f"Element at index {idx} is not iterable: {type(it).__name__!r}"
            )

    if source_weights is None:
        # Default: weight == source index, so lower index wins ties.
        weights = list(range(len(iterators)))
    else:
        weights = list(source_weights)
        if len(weights) != len(iterators):
            raise ValueError(
                f"source_weights length ({len(weights)}) must match "
                f"iterators length ({len(iterators)})"
            )

    # When source_weights are all equal to the default (0, 1, 2, …) and no
    # custom weights are supplied, heapq.merge already breaks ties by source
    # order.  However, to honour arbitrary weights we manage the heap ourselves.
    #
    # Heap entries: (value, weight, source_index, iterator)
    # Comparing (value, weight) is sufficient for a stable, weight-aware merge;
    # source_index is kept only for diagnostics / equal-weight tie-breaking.

    heap = []
    for idx, (it, w) in enumerate(zip(iterators, weights)):
        it = iter(it)
        try:
            value = next(it)
        except StopIteration:
            continue
        heapq.heappush(heap, (value, w, idx, it))

    while heap:
        value, w, idx, it = heapq.heappop(heap)
        yield value
        try:
            next_value = next(it)
        except StopIteration:
            continue
        heapq.heappush(heap, (next_value, w, idx, it))
