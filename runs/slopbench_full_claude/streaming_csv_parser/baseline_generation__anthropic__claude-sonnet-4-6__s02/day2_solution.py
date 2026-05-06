"""
streaming_csv_parser.py

Provides parse_csv_rows, a streaming CSV parser that yields dicts.
"""

import csv
from typing import Callable, Iterator, Optional


def parse_csv_rows(
    lines,
    normalize_header: Optional[Callable[[str], str]] = None,
) -> Iterator[dict]:
    """
    Parse a streaming iterable of strings as CSV.

    The first non-empty line is treated as the header row.
    Each subsequent non-empty line is yielded as a dict mapping
    header names to cell values.

    Parameters
    ----------
    lines : iterable of str
        Source lines (may be a generator or any iterable).
    normalize_header : callable or None, optional
        When provided, applied to each header cell after stripping
        whitespace.  When omitted, header cells are used as-is
        (after whitespace stripping), preserving original behavior.

    Yields
    ------
    dict[str, str]
        One dictionary per data row.
    """
    # Filter out empty lines while preserving streaming behaviour.
    non_empty = (line for line in lines if line.strip())

    reader = csv.reader(non_empty)

    # The first non-empty line is the header.
    try:
        headers = next(reader)
    except StopIteration:
        # No content at all – nothing to yield.
        return

    # Strip whitespace from header names for clean keys, then optionally
    # apply the caller-supplied normalisation function.
    headers = [h.strip() for h in headers]
    if normalize_header is not None:
        headers = [normalize_header(h) for h in headers]

    for row in reader:
        # Pair each header with the corresponding cell value.
        # csv.reader already handles quoted fields, embedded commas, etc.
        yield {header: (row[i].strip() if i < len(row) else "") for i, header in enumerate(headers)}
