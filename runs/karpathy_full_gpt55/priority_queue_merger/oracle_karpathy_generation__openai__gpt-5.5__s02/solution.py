import heapq
from collections.abc import Iterable, Iterator


def merge_sorted_iterators(iterators: list[Iterable[int]]) -> Iterator[int]:
    """Lazily merge sorted integer iterables into one sorted iterator."""
    heap: list[tuple[int, int, Iterator[int]]] = []
    counter = 0

    for iterable in iterators:
        iterator = iter(iterable)
        try:
            value = next(iterator)
        except StopIteration:
            continue
        heapq.heappush(heap, (value, counter, iterator))
        counter += 1

    while heap:
        value, _, iterator = heapq.heappop(heap)
        yield value

        try:
            next_value = next(iterator)
        except StopIteration:
            continue

        heapq.heappush(heap, (next_value, counter, iterator))
        counter += 1
