"""
A module for lazily merging sorted iterators.
"""

import heapq
from typing import Iterable, Iterator, List

__all__ = ["merge_sorted_iterators"]


def merge_sorted_iterators(iterators: List[Iterable[int]]) -> Iterator[int]:
    """
    Merges multiple sorted iterators into a single sorted iterator.

    This function takes a list of iterables, each of which is assumed to yield
    integers in non-decreasing order. It returns a new iterator that yields all
    elements from the input iterables in a single, sorted sequence.

    The merging is performed lazily using a min-heap. This means that memory
    usage is proportional to the number of input iterators, not the total
    number of elements.

    Args:
        iterators: A list of iterables. Each iterable must yield integers in
                   sorted (non-decreasing) order.

    Yields:
        Integers from the combined input iterators, in sorted order.

    Raises:
        TypeError: If an element in the input list is not iterable, or if
                   the iterables yield non-integer/non-comparable items.
    """
    min_heap = []
    live_iterators = [iter(it) for it in iterators]

    # Prime the heap with the first element from each non-empty iterator.
    for iterator_index, it in enumerate(live_iterators):
        try:
            first_value = next(it)
            # The heap stores tuples of (value, iterator_index, iterator).
            # The iterator_index acts as a tie-breaker to ensure heap elements
            # are unique and to maintain stability, which is good practice.
            heapq.heappush(min_heap, (first_value, iterator_index, it))
        except StopIteration:
            # This iterator is empty from the start.
            pass

    # The main loop continues as long as there are elements to process.
    while min_heap:
        value, iterator_index, current_iterator = heapq.heappop(min_heap)
        yield value

        try:
            next_value = next(current_iterator)
            heapq.heappush(
                min_heap, (next_value, iterator_index, current_iterator)
            )
        except StopIteration:
            # This iterator is now exhausted and is naturally removed from the heap
            # because we do not push it back on.
            pass
