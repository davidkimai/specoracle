"""
priority_queue_merger.py

Merges multiple sorted iterables into a single sorted iterator lazily,
using a min-heap (priority queue) for efficiency.
"""

import heapq


def merge_sorted_iterators(iterators, source_weights=None):
    """
    Merge sorted input iterators lazily into a single sorted output iterator.

    Parameters
    ----------
    iterators : list of iterable of int
        A list of iterables, each yielding integers in non-decreasing order.
    source_weights : list of int or None, optional
        A list of integer weights, one per iterator. When values tie, the
        iterator with the lower weight wins. If two iterators share the same
        weight, the one with the lower source index wins. When omitted (None),
        behaviour is equivalent to all weights being equal (lower source index
        wins on ties).

    Yields
    ------
    int
        Integers from all input iterables in non-decreasing (sorted) order,
        with ties broken first by source weight then by source index.
    """
    heap = []

    # Build effective weights: if not provided, use index as weight so that
    # the tiebreaker below handles everything uniformly.
    if source_weights is None:
        effective_weights = list(range(len(iterators)))
    else:
        effective_weights = list(source_weights)

    # Initialize the heap with the first element from each iterator.
    # Heap entries are tuples (value, weight, index, iterator) where weight
    # and then index are used as tiebreakers to avoid comparing iterators
    # directly.
    for index, iterable in enumerate(iterators):
        iterator = iter(iterable)
        weight = effective_weights[index]
        try:
            value = next(iterator)
            heapq.heappush(heap, (value, weight, index, iterator))
        except StopIteration:
            # Empty iterator; skip it.
            pass

    while heap:
        value, weight, index, iterator = heapq.heappop(heap)
        yield value
        try:
            next_value = next(iterator)
            heapq.heappush(heap, (next_value, weight, index, iterator))
        except StopIteration:
            # This iterator is exhausted; do not push it back.
            pass
