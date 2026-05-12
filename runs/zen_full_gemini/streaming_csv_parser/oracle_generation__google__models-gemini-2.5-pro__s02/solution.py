"""
A module for streaming parsing of simple comma-separated value (CSV) data.
"""

from typing import Dict, Iterable, Iterator, List


def _parse_csv_line(line: str) -> List[str]:
    """
    Parses a single comma-separated line into a list of stripped strings.

    Returns an empty list for an empty or whitespace-only line. This is a
    simplified parser and does not handle quoted fields containing commas.

    Args:
        line: The string line to parse.

    Returns:
        A list of strings representing the fields in the line.
    """
    stripped_line = line.strip()
    if not stripped_line:
        return []
    return [field.strip() for field in stripped_line.split(',')]


def parse_csv_rows(lines: Iterable[str]) -> Iterator[Dict[str, str]]:
    """
    Parses an iterable of CSV lines into an iterator of dictionaries.

    The first non-empty line is treated as the header. Subsequent non-empty
    lines are treated as data rows. Each yielded item is a dictionary mapping
    header fields to the corresponding row values.

    This function operates in a streaming fashion and does not load the entire
    input into memory.

    Args:
        lines: An iterable of strings, where each string is a line of CSV data.

    Yields:
        A dictionary mapping header names (str) to row values (str).

    Raises:
        ValueError: If the header contains duplicate field names.
        ValueError: If a data row has a different number of columns than the header.

    Note:
        If the input iterable is empty or contains only empty lines, this function
        will correctly yield no items.
    """
    lines_iterator = iter(lines)
    header: List[str] = []

    for line in lines_iterator:
        header = _parse_csv_line(line)
        if header:
            break

    if not header:
        return

    if len(header) != len(set(header)):
        raise ValueError("CSV header contains duplicate fields.")

    num_columns = len(header)

    for line in lines_iterator:
        row_values = _parse_csv_line(line)
        if not row_values:
            continue

        if len(row_values) != num_columns:
            raise ValueError(
                f"Row has {len(row_values)} columns, but header has {num_columns}."
            )

        yield dict(zip(header, row_values))
