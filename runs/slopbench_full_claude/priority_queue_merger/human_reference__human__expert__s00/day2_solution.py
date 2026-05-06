from __future__ import annotations

import heapq


def merge_sorted_iterators(iterators, source_weights=None):
    sources = [iter(source) for source in iterators]
    if source_weights is None:
        weights = list(range(len(sources)))
    else:
        weights = list(source_weights)

    heap = []
    for index, iterator in enumerate(sources):
        try:
            value = next(iterator)
        except StopIteration:
            continue
        heapq.heappush(heap, (value, weights[index], index))

    while heap:
        value, weight, index = heapq.heappop(heap)
        yield value
        try:
            next_value = next(sources[index])
            heapq.heappush(heap, (next_value, weights[index], index))
        except StopIteration:
            pass
