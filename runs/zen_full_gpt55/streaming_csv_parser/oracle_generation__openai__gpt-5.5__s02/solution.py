import csv
from collections.abc import Iterable, Iterator


__all__ = ["parse_csv_rows"]


def parse_csv_rows(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    if isinstance(lines, str):
        raise TypeError("lines must be an iterable of strings, not a single string")

    try:
        line_iterator = iter(lines)
    except TypeError as exc:
        raise TypeError("lines must be an iterable of strings") from exc

    return _parse_rows(line_iterator)


def _parse_rows(lines: Iterator[str]) -> Iterator[dict[str, str]]:
    non_empty_lines = _iter_non_empty_lines(lines)

    try:
        header_line_number, header_line = next(non_empty_lines)
    except StopIteration as exc:
        raise ValueError("CSV input does not contain a header line") from exc

    header = _parse_csv_line(header_line, header_line_number, "header")
    _validate_header(header, header_line_number)

    expected_cells = len(header)

    for line_number, line in non_empty_lines:
        row = _parse_csv_line(line, line_number, "row")

        if len(row) != expected_cells:
            raise ValueError(
                f"CSV row on line {line_number} has {len(row)} cells; "
                f"expected {expected_cells}"
            )

        yield dict(zip(header, row))


def _iter_non_empty_lines(lines: Iterator[str]) -> Iterator[tuple[int, str]]:
    for line_number, line in enumerate(lines, start=1):
        if not isinstance(line, str):
            raise TypeError(f"line {line_number} is not a string")

        if line.strip() == "":
            continue

        yield line_number, line


def _parse_csv_line(line: str, line_number: int, record_name: str) -> list[str]:
    reader = csv.reader([line], strict=True)

    try:
        return next(reader)
    except csv.Error as exc:
        raise ValueError(
            f"invalid CSV {record_name} on line {line_number}: {exc}"
        ) from exc


def _validate_header(header: list[str], line_number: int) -> None:
    if not header:
        raise ValueError(f"CSV header on line {line_number} is empty")

    empty_positions = [
        position
        for position, name in enumerate(header, start=1)
        if name == ""
    ]

    if empty_positions:
        positions = ", ".join(str(position) for position in empty_positions)
        raise ValueError(
            f"CSV header on line {line_number} contains empty field name "
            f"at position(s): {positions}"
        )

    duplicate_names = _duplicate_names(header)

    if duplicate_names:
        names = ", ".join(repr(name) for name in duplicate_names)
        raise ValueError(
            f"CSV header on line {line_number} contains duplicate field "
            f"name(s): {names}"
        )


def _duplicate_names(names: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []

    for name in names:
        if name in seen and name not in duplicates:
            duplicates.append(name)
        seen.add(name)

    return duplicates
