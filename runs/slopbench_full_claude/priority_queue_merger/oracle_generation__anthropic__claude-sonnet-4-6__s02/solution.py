"""
priority_queue_merger
---------------------
Merge an arbitrary number of sorted iterables into a single sorted iterator.
"""

import heapq


def merge_sorted_iterators(iterators):
    """Merge sorted input iterables lazily into a single sorted iterator.

    Parameters
    ----------
    iterators : list[iterable[int]]
        A list of iterables, each yielding integers in non-decreasing order.

    Yields
    ------
    int
        Values from all iterables in sorted order.

    Raises
    ------
    TypeError
        If *iterators* is not iterable or any element is not iterable.
    """
    if not hasattr(iterators, "__iter__"):
        raise TypeError(f"Expected an iterable of iterables, got {type(iterators)!r}")

    # Convert each element to an iterator up front so we catch bad inputs early.
    streams = []
    for index, source in enumerate(iterators):
        if not hasattr(source, "__iter__"):
            raise TypeError(
                f"Element at index {index} is not iterable: {type(source)!r}"
            )
        streams.append(iter(source))

    # Seed the heap with the first value from each non-empty stream.
    # Heap entries: (value, stream_index, iterator)
    # stream_index breaks ties deterministically without comparing iterators.
    heap = []
    for stream_index, stream in enumerate(streams):
        value = next(stream, None)
        if value is not None:
            heapq.heappush(heap, (value, stream_index, stream))

    while heap:
        value, stream_index, stream = heapq.heappop(heap)
        yield value
        next_value = next(stream, None)
        if next_value is not None:
            heapq.heappush(heap, (next_value, stream_index, stream))
