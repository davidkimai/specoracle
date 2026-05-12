import heapq
from collections.abc import Iterable, Iterator


def merge_sorted_iterators(iterators: list[Iterable[int]]) -> Iterator[int]:
    """Lazily merge sorted integer iterables into one sorted iterator."""
    heap: list[tuple[int, int, Iterator[int]]] = []

    for index, iterable in enumerate(iterators):
        iterator = iter(iterable)
        try:
            value = next(iterator)
        except StopIteration:
            continue
        heapq.heappush(heap, (value, index, iterator))

    while heap:
        value, index, iterator = heapq.heappop(heap)
        yield value
        try:
            next_value = next(iterator)
        except StopIteration:
            continue
        heapq.heappush(heap, (next_value, index, iterator))
