from collections.abc import Iterable, Iterator
import heapq
from typing import Optional


__all__ = ["merge_sorted_iterators"]


def merge_sorted_iterators(iterators: list[Iterable[int]]) -> Iterator[int]:
    """Merge sorted integer iterables into one lazy sorted iterator."""
    sources = _make_iterators(iterators)
    return _merge_sources(sources)


def _make_iterators(iterables: Iterable[Iterable[int]]) -> list[Iterator[int]]:
    try:
        return [_make_iterator(iterable, index) for index, iterable in enumerate(iterables)]
    except TypeError as exc:
        if "object is not iterable" in str(exc):
            raise TypeError("iterators must be an iterable of integer iterables") from exc
        raise


def _make_iterator(iterable: Iterable[int], index: int) -> Iterator[int]:
    try:
        return iter(iterable)
    except TypeError as exc:
        raise TypeError(f"item at index {index} must be an iterable of integers") from exc


def _merge_sources(sources: list[Iterator[int]]) -> Iterator[int]:
    heap: list[tuple[int, int]] = []
    last_values: list[Optional[int]] = [None] * len(sources)

    for index, source in enumerate(sources):
        first_value = _next_value(source, index, None)
        if first_value is None:
            continue

        value = first_value
        last_values[index] = value
        heapq.heappush(heap, (value, index))

    while heap:
        value, index = heapq.heappop(heap)
        yield value

        previous = last_values[index]
        next_value = _next_value(sources[index], index, previous)
        if next_value is None:
            continue

        last_values[index] = next_value
        heapq.heappush(heap, (next_value, index))


def _next_value(
    source: Iterator[int],
    index: int,
    previous: Optional[int],
) -> Optional[int]:
    try:
        value = next(source)
    except StopIteration:
        return None

    _require_int(value, index)

    if previous is not None and value < previous:
        raise ValueError(
            f"iterator at index {index} is not sorted: "
            f"{previous!r} is followed by {value!r}"
        )

    return value


def _require_int(value: object, index: int) -> None:
    if not isinstance(value, int):
        raise TypeError(
            f"iterator at index {index} yielded {value!r}; expected an integer"
        )
