"""
streaming_csv_parser.py

Provides parse_csv_rows, a streaming CSV parser that yields dicts from
header names to cell values without buffering the entire input.
"""

import csv
from typing import Dict, Iterator


def parse_csv_rows(lines) -> Iterator[Dict[str, str]]:
    """
    Parse CSV rows from an iterable of strings.

    The first non-empty line is treated as the comma-separated header.
    Each subsequent non-empty line is yielded as a dict mapping header
    names to cell values.

    Parameters
    ----------
    lines : iterable of str
        Source lines (may be a generator or any iterable).

    Yields
    ------
    dict[str, str]
        One dictionary per data row.
    """
    # Filter out empty lines while preserving streaming behaviour.
    non_empty = (line for line in lines if line.strip())

    # Use csv.reader on the filtered generator so that quoting, escaping,
    # and other RFC-4180 details are handled correctly.
    reader = csv.reader(non_empty)

    # The first non-empty line is the header.
    try:
        headers = next(reader)
    except StopIteration:
        # No non-empty lines at all – nothing to yield.
        return

    header_count = len(headers)

    for row in reader:
        # Pad short rows with empty strings; truncate over-long rows so
        # that the dict always has exactly the header keys.
        if len(row) < header_count:
            row = row + [""] * (header_count - len(row))
        yield dict(zip(headers, row[:header_count]))
