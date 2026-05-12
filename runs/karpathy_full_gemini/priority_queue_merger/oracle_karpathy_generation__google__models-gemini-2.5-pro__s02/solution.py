"""
A module for lazily merging sorted iterators using a min-heap.
"""

import heapq
from typing import Iterable, Iterator, List


def merge_sorted_iterators(iterators: List[Iterable[int]]) -> Iterator[int]:
    """
    Merges multiple sorted iterators into a single sorted iterator.

    This function takes a list of iterables, each assumed to be sorted in
    non-decreasing order, and returns a new iterator that yields all their
    elements in a single sorted sequence. The merging is done lazily,
    using a min-heap, which is memory-efficient as it only stores at most
    one element from each input iterator at any time.

    Args:
        iterators: A list of iterables, where each iterable yields integers
                   in sorted order.

    Yields:
        Integers in a single, sorted stream from all input iterables.
    """
    # A min-heap to store the next available element from each iterator.
    # Each item in the heap is a tuple: (value, iterator_index).
    # The iterator_index is used as a tie-breaker if values are equal and
    # to track which iterator the value came from.
    min_heap = []

    # Convert input iterables to iterator objects.
    live_iterators = [iter(it) for it in iterators]

    # Prime the heap with the first element from each non-empty iterator.
    for i, it in enumerate(live_iterators):
        try:
            first_value = next(it)
            heapq.heappush(min_heap, (first_value, i))
        except StopIteration:
            # This iterator is empty from the start.
            pass

    # Main loop: pull the smallest element, yield it, and replenish the heap
    # from the same source iterator.
    while min_heap:
        value, iterator_index = heapq.heappop(min_heap)
        yield value

        source_iterator = live_iterators[iterator_index]
        try:
            next_value = next(source_iterator)
            heapq.heappush(min_heap, (next_value, iterator_index))
        except StopIteration:
            # The source iterator is now exhausted. It will not be added back
            # to the heap.
            pass
