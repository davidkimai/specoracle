from collections.abc import Iterable, Iterator
from heapq import heappop, heappush
from itertools import count


def merge_sorted_iterators(iterators: list[Iterable[int]]) -> Iterator[int]:
    """
    Lazily merge multiple sorted iterables of integers into one sorted iterator.

    Each input iterable is consumed only as needed.
    """
    heap: list[tuple[int, int, Iterator[int]]] = []
    sequence = count()

    for iterable in iterators:
        iterator = iter(iterable)
        try:
            first_value = next(iterator)
        except StopIteration:
            continue
        heappush(heap, (first_value, next(sequence), iterator))

    while heap:
        value, _, iterator = heappop(heap)
        yield value

        try:
            next_value = next(iterator)
        except StopIteration:
            continue
        heappush(heap, (next_value, next(sequence), iterator))


__all__ = ["merge_sorted_iterators"]
