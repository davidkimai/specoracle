from __future__ import annotations

import csv
from collections.abc import Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    if isinstance(lines, (str, bytes, bytearray)):
        raise TypeError("lines must be an iterable of strings, not a single string")

    try:
        iterator = iter(lines)
    except TypeError as exc:
        raise TypeError("lines must be an iterable of strings") from exc

    reader = csv.reader(_validated_lines(iterator), strict=True)
    return _records_from_reader(reader)


def _validated_lines(lines: Iterator[str]) -> Iterator[str]:
    for line_number, line in enumerate(lines, start=1):
        if not isinstance(line, str):
            raise TypeError(
                f"line {line_number} must be a string, got {type(line).__name__}"
            )
        yield line


def _records_from_reader(reader: csv.reader) -> Iterator[dict[str, str]]:
    header = _read_header(reader)
    if header is None:
        return

    _validate_header(header)

    for row in reader:
        if _is_empty_record(row):
            continue

        if len(row) != len(header):
            raise ValueError(
                f"CSV row ending at line {reader.line_num} has {len(row)} cells; "
                f"expected {len(header)}"
            )

        yield dict(zip(header, row))


def _read_header(reader: csv.reader) -> list[str] | None:
    for row in reader:
        if not _is_empty_record(row):
            return row
    return None


def _is_empty_record(row: list[str]) -> bool:
    return len(row) == 0


def _validate_header(header: list[str]) -> None:
    if not header:
        raise ValueError("CSV header must contain at least one column")

    empty_positions = [index + 1 for index, name in enumerate(header) if name == ""]
    if empty_positions:
        positions = ", ".join(str(position) for position in empty_positions)
        raise ValueError(f"CSV header contains empty column name at position(s): {positions}")

    seen: set[str] = set()
    duplicates: list[str] = []

    for name in header:
        if name in seen and name not in duplicates:
            duplicates.append(name)
        seen.add(name)

    if duplicates:
        names = ", ".join(repr(name) for name in duplicates)
        raise ValueError(f"CSV header contains duplicate column name(s): {names}")
