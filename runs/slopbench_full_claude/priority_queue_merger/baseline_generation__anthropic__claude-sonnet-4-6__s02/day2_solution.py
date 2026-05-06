"""
priority_queue_merger.py

Merges multiple sorted iterables into a single lazily-evaluated sorted iterator
using a min-heap (priority queue).
"""

import heapq
from typing import Iterable, Iterator


def merge_sorted_iterators(
    iterators: list[Iterable[int]],
    source_weights: list[int] | None = None,
) -> Iterator[int]:
    """
    Merge multiple sorted iterables into a single sorted iterator.

    Parameters
    ----------
    iterators : list of sorted iterables of int
        Each iterable must already be sorted in ascending order.
    source_weights : list of int or None, optional
        When two values are equal the iterator with the lower weight wins.
        If omitted (or None), the lower source index acts as the tiebreaker,
        which is equivalent to every source having weight equal to its index.

    Yields
    ------
    int
        Values from all input iterables in sorted (ascending) order.
    """
    if source_weights is None:
        # Default: use source index as weight so tiebreaking matches original
        # behaviour (lower index wins).
        weights = list(range(len(iterators)))
    else:
        weights = list(source_weights)

    heap: list[tuple[int, int, int, Iterator[int]]] = []

    # Initialise the heap with the first element from each iterator.
    # The tuple stored is (value, weight, source_index, iterator).
    # - weight is used as the primary tiebreaker after value.
    # - source_index is used as a secondary tiebreaker so that equal weights
    #   still resolve deterministically without ever comparing iterators
    #   (which would raise TypeError).
    for source_index, iterable in enumerate(iterators):
        it = iter(iterable)
        try:
            first_value = next(it)
        except StopIteration:
            continue  # empty iterable – skip
        heapq.heappush(heap, (first_value, weights[source_index], source_index, it))

    while heap:
        value, weight, source_index, it = heapq.heappop(heap)
        yield value
        try:
            next_value = next(it)
        except StopIteration:
            continue  # this iterator is exhausted
        heapq.heappush(heap, (next_value, weight, source_index, it))
