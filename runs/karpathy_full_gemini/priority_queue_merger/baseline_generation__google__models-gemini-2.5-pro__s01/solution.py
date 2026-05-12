"""
A module for lazily merging multiple sorted iterators.
"""

import heapq
from typing import Iterable, Iterator, List, Tuple

def merge_sorted_iterators(iterators: List[Iterable[int]]) -> Iterator[int]:
    """
    Merges multiple sorted iterators into a single sorted iterator.

    This function takes a list of iterables, each of which is assumed to yield
    integers in non-decreasing order. It returns a new iterator that yields all
    elements from the input iterators in a single, sorted sequence.

    The merging process is performed lazily, meaning that elements are only
    fetched from the input iterators as they are needed. This makes the
    function memory-efficient, especially for large input sequences. A min-heap
    is used to efficiently determine the next smallest element across all
    iterators.

    Args:
        iterators: A list of iterables, where each iterable yields integers
                   in sorted (non-decreasing) order.

    Yields:
        Integers in a single, sorted stream, combined from all input
        iterators.
    """
    # Min-heap to store tuples of:
    # (current_value, source_iterator_index, source_iterator)
    # The source_iterator_index is used as a tie-breaker to ensure heap elements
    # are always comparable, even if values are equal. This prevents errors
    # that can arise from comparing iterator objects directly.
    min_heap: List[Tuple[int, int, Iterator[int]]] = []

    # Convert all iterables to iterators to ensure consistent `next()` behavior.
    iterator_list = [iter(it) for it in iterators]

    # Prime the heap with the first element from each non-empty iterator.
    for i, it in enumerate(iterator_list):
        try:
            first_value = next(it)
            heapq.heappush(min_heap, (first_value, i, it))
        except StopIteration:
            # This iterator is empty, so we don't add it to the heap.
            pass

    # While the heap is not empty, there are still elements to process.
    while min_heap:
        # Pop the smallest element. The heap property ensures this is the
        # smallest element currently available across all iterators.
        value, index, current_iterator = heapq.heappop(min_heap)

        # Yield the smallest value to the consumer.
        yield value

        # Try to get the next element from the same iterator we just
        # pulled from and push it back onto the heap.
        try:
            next_value = next(current_iterator)
            heapq.heappush(min_heap, (next_value, index, current_iterator))
        except StopIteration:
            # This iterator is now exhausted. We simply don't add it back
            # to the heap, effectively removing it from consideration.
            pass
