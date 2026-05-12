from collections.abc import Iterable, Iterator
from itertools import count
import heapq


def merge_sorted_iterators(iterators: list[Iterable[int]]) -> Iterator[int]:
    """
    Lazily merge multiple sorted iterables of integers into one sorted iterator.

    Each input iterable is advanced only as needed: at most one pending value is
    held from each iterable at any time.
    """
    heap: list[tuple[int, int, Iterator[int]]] = []
    tie_breaker = count()

    for iterable in iterators:
        iterator = iter(iterable)
        try:
            first_value = next(iterator)
        except StopIteration:
            continue
        heapq.heappush(heap, (first_value, next(tie_breaker), iterator))

    while heap:
        value, _, iterator = heapq.heappop(heap)
        yield value

        try:
            next_value = next(iterator)
        except StopIteration:
            continue

        heapq.heappush(heap, (next_value, next(tie_breaker), iterator))
