from __future__ import annotations

import heapq
from collections.abc import Iterable, Iterator
from dataclasses import dataclass


@dataclass
class _SourceState:
    index: int
    iterator: Iterator[int]
    has_last_value: bool = False
    last_value: int = 0


def merge_sorted_iterators(iterators: list[Iterable[int]]) -> Iterator[int]:
    if not isinstance(iterators, list):
        raise TypeError("iterators must be a list of iterables")

    sources = tuple(iterators)
    return _merge_sources(sources)


def _merge_sources(sources: tuple[Iterable[int], ...]) -> Iterator[int]:
    states = [_make_state(index, source) for index, source in enumerate(sources)]
    heap: list[tuple[int, int]] = []

    for state in states:
        value = _read_next(state)
        if value is not None:
            heapq.heappush(heap, (value, state.index))

    while heap:
        value, index = heapq.heappop(heap)
        yield value

        next_value = _read_next(states[index])
        if next_value is not None:
            heapq.heappush(heap, (next_value, index))


def _make_state(index: int, source: Iterable[int]) -> _SourceState:
    try:
        iterator = iter(source)
    except TypeError as exc:
        raise TypeError(f"iterators[{index}] must be iterable") from exc

    return _SourceState(index=index, iterator=iterator)


def _read_next(state: _SourceState) -> int | None:
    try:
        value = next(state.iterator)
    except StopIteration:
        return None

    _require_int(state.index, value)

    if state.has_last_value and value < state.last_value:
        raise ValueError(
            f"iterators[{state.index}] is not sorted: "
            f"yielded {value!r} after {state.last_value!r}"
        )

    state.last_value = value
    state.has_last_value = True
    return value


def _require_int(index: int, value: object) -> None:
    if not isinstance(value, int):
        raise TypeError(
            f"iterators[{index}] yielded {type(value).__name__}; expected int"
        )


__all__ = ["merge_sorted_iterators"]
