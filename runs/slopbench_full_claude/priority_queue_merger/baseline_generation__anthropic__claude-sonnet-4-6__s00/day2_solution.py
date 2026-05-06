"""
priority_queue_merger.py

Merges multiple sorted iterables into a single sorted iterator lazily,
using a min-heap (priority queue) for efficient merging.
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
        Each iterable must yield integers in non-decreasing order.
    source_weights : list of int or None, optional
        When two values tie, the source with the lower weight wins.
        If omitted (or None), the lower source index is used as the
        tiebreaker (preserving the original behaviour).

    Yields
    ------
    int
        Integers from all input iterables in non-decreasing order.
    """
    if source_weights is not None and len(source_weights) != len(iterators):
        raise ValueError(
            "source_weights must have the same length as iterators"
        )

    # heap entries: (value, tiebreaker, iterator_index, iterator)
    # tiebreaker is either the caller-supplied weight or the source index,
    # ensuring we never need to compare iterator objects directly.
    heap: list[tuple[int, int, int, Iterator[int]]] = []

    for idx, iterable in enumerate(iterators):
        tiebreaker = source_weights[idx] if source_weights is not None else idx
        it = iter(iterable)
        try:
            value = next(it)
            heapq.heappush(heap, (value, tiebreaker, idx, it))
        except StopIteration:
            # Empty iterable — skip it
            pass

    while heap:
        value, tiebreaker, idx, it = heapq.heappop(heap)
        yield value
        try:
            next_value = next(it)
            heapq.heappush(heap, (next_value, tiebreaker, idx, it))
        except StopIteration:
            # This iterator is exhausted — don't re-push it
            pass
