from __future__ import annotations

from collections.abc import Iterable, Iterator
from heapq import heappop, heappush


def merge_sorted_iterators(iterators: list[Iterable[int]]) -> Iterator[int]:
    if not isinstance(iterators, list):
        raise TypeError("iterators must be a list of iterable objects")

    sources = _as_iterators(iterators)
    return _merge_sources(sources)


def _as_iterators(iterables: list[Iterable[int]]) -> list[Iterator[int]]:
    sources: list[Iterator[int]] = []

    for index, iterable in enumerate(iterables):
        try:
            sources.append(iter(iterable))
        except TypeError as error:
            raise TypeError(f"item at index {index} is not iterable") from error

    return sources


def _merge_sources(sources: list[Iterator[int]]) -> Iterator[int]:
    heap: list[tuple[int, int]] = []
    last_values: list[int | None] = [None] * len(sources)
    has_last_value = [False] * len(sources)

    for source_index, source in enumerate(sources):
        has_value, value = _next_checked(
            source,
            source_index,
            last_values,
            has_last_value,
        )
        if has_value:
            heappush(heap, (value, source_index))

    while heap:
        value, source_index = heappop(heap)
        yield value

        has_value, next_value = _next_checked(
            sources[source_index],
            source_index,
            last_values,
            has_last_value,
        )
        if has_value:
            heappush(heap, (next_value, source_index))


def _next_checked(
    source: Iterator[int],
    source_index: int,
    last_values: list[int | None],
    has_last_value: list[bool],
) -> tuple[bool, int]:
    try:
        value = next(source)
    except StopIteration:
        return False, 0

    _validate_int(value, source_index)

    if has_last_value[source_index]:
        last_value = last_values[source_index]
        if last_value is not None and value < last_value:
            raise ValueError(f"iterator at index {source_index} is not sorted")

    last_values[source_index] = value
    has_last_value[source_index] = True
    return True, value


def _validate_int(value: object, source_index: int) -> None:
    if type(value) is not int:
        raise TypeError(
            f"iterator at index {source_index} yielded a non-int value: {value!r}"
        )
