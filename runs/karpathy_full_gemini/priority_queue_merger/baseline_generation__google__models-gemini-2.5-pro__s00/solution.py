"""
A module for lazily merging sorted iterators.
"""

import heapq
from typing import Iterable, Iterator, List

def merge_sorted_iterators(iterators: List[Iterable[int]]) -> Iterator[int]:
    """
    Merges multiple sorted iterators into a single sorted iterator.

    This function takes a list of iterables, each of which is assumed to yield
    integers in non-decreasing order. It returns a new iterator that yields all
    elements from the input iterables in a single, sorted, non-decreasing
    sequence.

    The merging is performed lazily, meaning that elements are only fetched
    from the input iterators as needed. This makes the function memory-efficient,
    especially for large input streams. It uses a min-heap to efficiently find
    the next smallest element across all iterators.

    Args:
        iterators: A list of iterables, where each iterable yields integers
                   in sorted (non-decreasing) order.

    Yields:
        Integers in a single, sorted stream.
    """
    # Min-heap to store the next available element from each iterator.
    # Each item in the heap is a tuple: (value, iterator_index, iterator_obj).
    # The iterator_index is used as a tie-breaker to ensure stable sorting
    # and to prevent comparing iterator objects, which would raise a TypeError.
    min_heap = []

    # Convert all input iterables to iterators.
    iter_list = [iter(it) for it in iterators]

    # Prime the heap with the first element from each non-empty iterator.
    for i, it in enumerate(iter_list):
        try:
            first_val = next(it)
            heapq.heappush(min_heap, (first_val, i, it))
        except StopIteration:
            # The iterator is empty, so we ignore it.
            pass

    # Process the heap until it's empty.
    while min_heap:
        # Get the smallest element currently available.
        val, i, it = heapq.heappop(min_heap)
        yield val

        # Try to get the next element from the same iterator and add it back to the heap.
        try:
            next_val = next(it)
            heapq.heappush(min_heap, (next_val, i, it))
        except StopIteration:
            # This iterator is exhausted; it will not be added back to the heap.
            pass
