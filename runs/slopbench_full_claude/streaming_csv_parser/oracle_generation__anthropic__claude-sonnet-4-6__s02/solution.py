"""
streaming_csv_parser.py

Streaming CSV parser that yields row dictionaries from an iterable of lines.
"""

import csv


def parse_csv_rows(lines):
    """Parse an iterable of strings as CSV, yielding one dict per data row.

    The first non-empty line is treated as the header.
    Each subsequent non-empty line is yielded as a dict mapping header names
    to cell values.

    Args:
        lines: An iterable of strings (with or without newline characters).

    Yields:
        dict[str, str]: One dictionary per data row.

    Raises:
        ValueError: If a data row has a different number of fields than the header.
    """
    non_empty = (line for line in lines if line.strip())
    reader = csv.reader(non_empty)

    try:
        header = next(reader)
    except StopIteration:
        return

    for row in reader:
        if len(row) != len(header):
            raise ValueError(
                f"Row has {len(row)} field(s), expected {len(header)}: {row!r}"
            )
        yield dict(zip(header, row))
