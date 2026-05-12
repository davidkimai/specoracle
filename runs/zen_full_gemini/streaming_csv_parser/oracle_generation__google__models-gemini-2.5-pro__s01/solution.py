"""A module for streaming parsing of simple, comma-separated value (CSV) data."""

from typing import Dict, Iterable, Iterator, List, Optional

__all__ = ["parse_csv_rows"]


def _parse_line(line: str) -> Optional[List[str]]:
    """
    Parses a single line of CSV text.

    This helper handles stripping whitespace from the line and from each
    resulting field. It returns None for lines that are empty or contain
    only whitespace, effectively skipping them.

    Args:
        line: The string line to parse.

    Returns:
        A list of strings representing the fields, or None if the line is empty.
    """
    stripped_line = line.strip()
    if not stripped_line:
        return None
    return [field.strip() for field in stripped_line.split(',')]


def parse_csv_rows(lines: Iterable[str]) -> Iterator[Dict[str, str]]:
    """
    Parses an iterable of CSV lines into an iterator of dictionaries.

    The first non-empty line is treated as the header. Subsequent non-empty
    lines are data rows. The keys of the yielded dictionaries are the header
    fields. This function operates in a streaming fashion and does not load
    the entire input into memory.

    Args:
        lines: An iterable of strings, where each string is a line of CSV data.

    Yields:
        A dictionary representing a row, mapping header fields to values.

    Raises:
        ValueError: If a data row has a different number of columns than the
                    header.
    """
    lines_iterator = iter(lines)
    header: Optional[List[str]] = None
    header_line_number = 0

    for i, line in enumerate(lines_iterator, start=1):
        header_fields = _parse_line(line)
        if header_fields is not None:
            header = header_fields
            header_line_number = i
            break

    if header is None:
        return  # No content, yield nothing.

    num_columns = len(header)

    for i, line in enumerate(lines_iterator, start=header_line_number + 1):
        row_values = _parse_line(line)
        if row_values is None:
            continue  # Skip empty or whitespace-only lines.

        if len(row_values) != num_columns:
            raise ValueError(
                f"Line {i}: expected {num_columns} columns, but found "
                f"{len(row_values)}"
            )

        yield dict(zip(header, row_values))
