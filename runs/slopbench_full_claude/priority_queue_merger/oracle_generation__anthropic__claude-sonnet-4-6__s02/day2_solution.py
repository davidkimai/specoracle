"""
priority_queue_merger
---------------------
Merge an arbitrary number of sorted iterables into a single sorted iterator.
"""

import heapq


def merge_sorted_iterators(iterators, source_weights=None):
    """Merge sorted input iterables lazily into a single sorted iterator.

    Parameters
    ----------
    iterators : list[iterable[int]]
        A list of iterables, each yielding integers in non-decreasing order.
    source_weights : list[int] | None, optional
        A list of integer weights, one per iterable.  When two values tie the
        iterable with the *lower* weight is yielded first.  If omitted (or
        ``None``) the source index is used as the weight, so lower-indexed
        sources win ties – preserving the original behaviour.

    Yields
    ------
    int
        Values from all iterables in sorted order.

    Raises
    ------
    TypeError
        If *iterators* is not iterable or any element is not iterable.
    ValueError
        If *source_weights* is provided but its length differs from the number
        of iterables.
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

    # Resolve weights: default to source index when not supplied.
    if source_weights is None:
        weights = list(range(len(streams)))
    else:
        weights = list(source_weights)
        if len(weights) != len(streams):
            raise ValueError(
                f"source_weights length ({len(weights)}) must match the number "
                f"of iterables ({len(streams)})"
            )

    # Seed the heap with the first value from each non-empty stream.
    # Heap entries: (value, weight, stream_index, iterator)
    # weight is the primary tie-breaker; stream_index is the secondary
    # tie-breaker so that iterator objects are never compared.
    heap = []
    for stream_index, stream in enumerate(streams):
        value = next(stream, None)
        if value is not None:
            heapq.heappush(heap, (value, weights[stream_index], stream_index, stream))

    while heap:
        value, weight, stream_index, stream = heapq.heappop(heap)
        yield value
        next_value = next(stream, None)
        if next_value is not None:
            heapq.heappush(heap, (next_value, weights[stream_index], stream_index, stream))
