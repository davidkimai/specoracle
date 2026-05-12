from __future__ import annotations

import csv
from collections.abc import Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    if isinstance(lines, (str, bytes)):
        raise TypeError("lines must be an iterable of strings, not a single string")

    try:
        line_iterator = iter(lines)
    except TypeError as exc:
        raise TypeError("lines must be an iterable of strings") from exc

    return _parse_csv_rows(line_iterator)


def _parse_csv_rows(lines: Iterator[str]) -> Iterator[dict[str, str]]:
    reader = csv.reader(_non_empty_lines(lines), strict=True)
    header = _read_header(reader)
    _validate_header(header)

    row_number = 1
    while True:
        row_number += 1
        try:
            row = next(reader)
        except StopIteration:
            return
        except csv.Error as exc:
            raise ValueError(f"invalid CSV row {row_number}: {exc}") from exc

        yield _make_row(header, row, row_number)


def _non_empty_lines(lines: Iterator[str]) -> Iterator[str]:
    for line in lines:
        if not isinstance(line, str):
            raise TypeError("lines must contain only strings")
        if line.strip():
            yield line


def _read_header(reader: csv.reader) -> list[str]:
    try:
        return next(reader)
    except StopIteration as exc:
        raise ValueError("lines must contain a non-empty header line") from exc
    except csv.Error as exc:
        raise ValueError(f"invalid CSV header: {exc}") from exc


def _validate_header(header: list[str]) -> None:
    if not header:
        raise ValueError("header must contain at least one column")

    empty_positions = [index + 1 for index, name in enumerate(header) if name == ""]
    if empty_positions:
        positions = ", ".join(str(position) for position in empty_positions)
        raise ValueError(f"header contains empty column names at positions: {positions}")

    duplicates = _duplicate_names(header)
    if duplicates:
        names = ", ".join(repr(name) for name in duplicates)
        raise ValueError(f"header contains duplicate column names: {names}")


def _duplicate_names(names: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []

    for name in names:
        if name in seen and name not in duplicates:
            duplicates.append(name)
        seen.add(name)

    return duplicates


def _make_row(header: list[str], row: list[str], row_number: int) -> dict[str, str]:
    if len(row) != len(header):
        raise ValueError(
            f"row {row_number} has {len(row)} cells; expected {len(header)}"
        )

    return dict(zip(header, row))
