"""A module for lazily merging multiple sorted iterators."""

import heapq
from typing import Iterable, Iterator, List, Tuple


def _initialize_heap(
    iterator_list: List[Iterator[int]],
) -> List[Tuple[int, int]]:
    """
    Creates and primes a min-heap with the first element of each iterator.

    Args:
        iterator_list: A list of iterators to draw initial elements from.

    Returns:
        A min-heap containing tuples of (first_value, iterator_index) for
        each non-empty iterator.
    """
    min_heap: List[Tuple[int, int]] = []
    for i, it in enumerate(iterator_list):
        try:
            first_value = next(it)
            # The item pushed to the heap is a tuple of (value, iterator_index).
            # The value is used for sorting, and the index to track the source.
            # Using an index as a tie-breaker also ensures stability.
            heapq.heappush(min_heap, (first_value, i))
        except StopIteration:
            # This iterator is empty, so it contributes nothing to the heap.
            pass
    return min_heap


def merge_sorted_iterators(iterators: List[Iterable[int]]) -> Iterator[int]:
    """
    Merges multiple sorted iterators into a single lazy sorted iterator.

    This function uses a min-heap to efficiently find the smallest next element
    across all iterators. It is lazy, meaning it only pulls elements from the
    input iterators as they are needed, making it suitable for very large or
    infinite sequences.

    Args:
        iterators: A list of iterables, where each is expected to yield
                   integers in non-decreasing order.

    Yields:
        Integers from all input iterators in a single sorted sequence.

    Raises:
        TypeError: If the top-level input is not a list, or if elements
                   within the iterators are not comparable.
    """
    if not isinstance(iterators, list):
        raise TypeError("Input must be a list of iterables.")

    # Convert all provided iterables to stateful iterators to allow `next()`.
    iterator_list = [iter(it) for it in iterators]

    # Prime the heap with the first element from each non-empty iterator.
    min_heap = _initialize_heap(iterator_list)

    # The main loop continues as long as there are elements in the heap.
    # An empty heap signifies that all input iterators are exhausted.
    while min_heap:
        # Pop the smallest available element. The heap property ensures this
        # is the smallest among the current heads of all active iterators.
        value, iterator_index = heapq.heappop(min_heap)

        yield value

        # Identify the iterator from which the element was taken.
        source_iterator = iterator_list[iterator_index]

        # Try to replenish the heap with the next element from that iterator.
        try:
            next_value = next(source_iterator)
            heapq.heappush(min_heap, (next_value, iterator_index))
        except StopIteration:
            # This iterator is exhausted and will not be added back to the
            # heap, effectively removing it from the merge process.
            pass
