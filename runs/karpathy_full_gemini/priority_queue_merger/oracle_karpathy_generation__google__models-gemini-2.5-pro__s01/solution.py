"""
A Python module for lazily merging multiple sorted iterators.
"""

import heapq
from typing import Iterable, Iterator, List


def merge_sorted_iterators(iterables: List[Iterable[int]]) -> Iterator[int]:
    """Merges multiple sorted iterators into a single sorted iterator.

    This function takes a list of iterables, each of which is assumed to yield
    integers in non-decreasing order. It returns a new iterator that yields all
    the elements from the input iterables in a single, sorted sequence.

    The merging is performed lazily using a min-heap. This means that the
    function does not pull all elements into memory at once, making it suitable
    for very large input streams. At any time, it only stores at most one
    element from each input iterable.

    Args:
        iterables: A list of iterables, where each iterable is sorted in
            non-decreasing order.

    Yields:
        Integers in sorted order from the merged iterables.
    """
    min_heap = []
    
    # Convert all provided iterables into iterators.
    iterator_list = [iter(it) for it in iterables]
    
    # Initialize the min-heap with the first element from each non-empty iterator.
    # The heap stores tuples of (value, iterator_index). The index is used
    # to identify which iterator to pull the next element from.
    for i, it in enumerate(iterator_list):
        try:
            first_value = next(it)
            heapq.heappush(min_heap, (first_value, i))
        except StopIteration:
            # The iterator is empty from the start, so we simply ignore it.
            pass
            
    # As long as the heap is not empty, there are still elements to process.
    while min_heap:
        # Pop the smallest element currently available from all iterators.
        value, it_index = heapq.heappop(min_heap)
        
        yield value
        
        # Get the iterator from which the smallest element was taken.
        source_iterator = iterator_list[it_index]
        
        # Try to get the next element from this iterator and add it to the heap.
        try:
            next_value = next(source_iterator)
            heapq.heappush(min_heap, (next_value, it_index))
        except StopIteration:
            # This iterator is now exhausted; we do nothing, and it will no
            # longer contribute elements to the heap.
            pass
