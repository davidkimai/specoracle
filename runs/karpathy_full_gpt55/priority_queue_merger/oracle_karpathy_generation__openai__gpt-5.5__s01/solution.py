from collections.abc import Iterable, Iterator
import heapq


def merge_sorted_iterators(iterators: list[Iterable[int]]) -> Iterator[int]:
    return heapq.merge(*iterators)
