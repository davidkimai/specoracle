"""
A module for lazily merging multiple sorted iterators.
"""

import heapq
from typing import Iterable, Iterator, List


def merge_sorted_iterators(iterators: List[Iterable[int]]) -> Iterator[int]:
    """
    Merges multiple sorted iterators into a single sorted iterator.

    This function takes a list of iterables, each assumed to yield integers
    in non-decreasing order. It returns a new iterator that yields all
    elements from the input iterables in a single, sorted sequence.

    The merging is performed lazily using a min-heap, consuming memory
    proportional to the number of input iterators, not the total number
    of elements.

    Args:
        iterators: A list of iterables, where each iterable is already sorted.

    Yields:
        Integers in sorted order from the merged iterators.

    Raises:
        TypeError: If the input is not a list of iterables, or if the
                   elements of the iterables are not comparable.
    """
    # The min-heap stores tuples of (value, source_index, source_iterator).
    # The `source_index` acts as a tie-breaker to ensure a stable sort order
    # and to prevent comparison errors between non-comparable iterator objects.
    min_heap = []

    # Eagerly convert all input iterables to iterators to handle state consistently.
    active_iterators = [iter(it) for it in iterators]

    # Prime the heap with the first element from each non-empty iterator.
    for i, it in enumerate(active_iterators):
        try:
            first_value = next(it)
            heap_item = (first_value, i, it)
            heapq.heappush(min_heap, heap_item)
        except StopIteration:
            # This iterator was empty from the start, so we ignore it.
            pass

    # The main merging loop continues as long as there are elements in the heap.
    while min_heap:
        # Get the smallest item currently available from all source iterators.
        value, source_index, source_iterator = heapq.heappop(min_heap)

        yield value

        # Try to pull the next item from the iterator we just took from.
        # If successful, add it to the heap. If the iterator is exhausted,
        # the StopIteration exception is caught, and we simply move on.
        try:
            next_value = next(source_iterator)
            next_heap_item = (next_value, source_index, source_iterator)
            heapq.heappush(min_heap, next_heap_item)
        except StopIteration:
            # This iterator is now exhausted and will be dropped from consideration.
            pass
