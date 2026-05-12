"""
A module for lazily merging sorted iterators.
"""

import heapq
from typing import List, Iterable, Iterator

def merge_sorted_iterators(iterators: List[Iterable[int]]) -> Iterator[int]:
    """
    Merges multiple sorted iterators into a single sorted iterator.

    This function takes a list of iterables, each of which is assumed to
    yield integers in non-decreasing order. It returns a new iterator that
    yields all elements from the input iterables in a single, sorted sequence.

    The merging is done lazily, using a min-heap to keep track of the next
    available element from each iterator. This makes it memory-efficient,
    especially for large input streams.

    Args:
        iterators: A list of iterables, where each iterable yields sorted integers.

    Yields:
        Integers in sorted order from the merged iterators.
    """
    min_heap = []
    
    # The heap stores tuples of (value, iterator_index, iterator_object).
    # The iterator_index is used as a tie-breaker to ensure stability and
    # prevent comparison errors between non-comparable iterator objects in Python 3.
    for i, it in enumerate(map(iter, iterators)):
        try:
            first_val = next(it)
            heapq.heappush(min_heap, (first_val, i, it))
        except StopIteration:
            # This iterator is empty, so we just skip it.
            pass

    while min_heap:
        # Get the smallest element currently available from all iterators.
        val, i, it = heapq.heappop(min_heap)
        yield val

        # Try to push the next element from the same iterator back into the heap.
        try:
            next_val = next(it)
            heapq.heappush(min_heap, (next_val, i, it))
        except StopIteration:
            # This iterator is exhausted. We don't add it back to the heap.
            pass
