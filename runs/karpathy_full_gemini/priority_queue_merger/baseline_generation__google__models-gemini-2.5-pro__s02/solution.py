# -*- coding: utf-8 -*-
"""
A module for lazily merging sorted iterators.
"""

import heapq
from typing import Iterable, Iterator, List

__all__ = ["merge_sorted_iterators"]


def merge_sorted_iterators(
    iterators: List[Iterable[int]],
) -> Iterator[int]:
    """
    Merges multiple sorted iterators into a single sorted iterator.

    This function takes a list of iterables, each of which is assumed to yield
    integers in non-decreasing order. It returns a new iterator that yields all
    elements from the input iterables in a single, sorted sequence.

    The merging is performed lazily using a min-heap, which is efficient in
    terms of both time and memory. It only keeps at most one element from each
    input iterator in memory at any given time.

    Args:
        iterators: A list of iterables, where each iterable yields integers
                   in sorted (non-decreasing) order.

    Yields:
        Integers in sorted (non-decreasing) order from the merged iterators.

    Example:
        >>> it1 = iter([1, 5, 10])
        >>> it2 = iter([2, 3, 8])
        >>> it3 = iter([4, 9])
        >>> merged = merge_sorted_iterators([it1, it2, it3])
        >>> list(merged)
        [1, 2, 3, 4, 5, 8, 9, 10]
    """
    # Min-heap to store the next available element from each iterator.
    # Each element in the heap is a tuple: (value, iterator_index, iterator_object)
    # The iterator_index is used as a tie-breaker to ensure heap elements are
    # always comparable, even if values are equal. This prevents comparison
    # errors on the iterator objects themselves.
    min_heap = []

    # Initialize the heap with the first element from each non-empty iterator.
    for i, it_iterable in enumerate(iterators):
        it = iter(it_iterable)
        try:
            first_val = next(it)
            heapq.heappush(min_heap, (first_val, i, it))
        except StopIteration:
            # The iterator is empty, so we ignore it.
            pass

    # Main loop: extract the minimum element, yield it, and push the next
    # element from the same iterator onto the heap.
    while min_heap:
        val, i, it = heapq.heappop(min_heap)
        yield val
        try:
            next_val = next(it)
            heapq.heappush(min_heap, (next_val, i, it))
        except StopIteration:
            # This iterator is exhausted and will not be added back to the heap.
            pass
