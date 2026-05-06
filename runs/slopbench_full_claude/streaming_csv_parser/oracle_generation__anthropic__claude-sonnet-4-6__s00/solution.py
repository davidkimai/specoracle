"""
streaming_csv_parser.py

Streaming CSV parser that yields header-keyed dicts for each data row.
"""

import csv


def parse_csv_rows(lines):
    """
    Parse a streaming iterable of strings as CSV.

    The first non-empty line is treated as the header row.
    Each subsequent non-empty line is yielded as a dict mapping
    header names to cell values.

    Parameters
    ----------
    lines : iterable[str]
        Raw lines of CSV text (with or without trailing newlines).

    Yields
    ------
    dict[str, str]
        One dictionary per data row.

    Raises
    ------
    ValueError
        If the input contains no non-empty lines (no header found),
        or if a data row has a different number of fields than the header.
    """
    non_empty = (line for line in lines if line.strip())
    reader = csv.reader(non_empty)

    try:
        header = next(reader)
    except StopIteration:
        raise ValueError("Input contains no non-empty lines; cannot determine header.")

    num_fields = len(header)

    for row_number, row in enumerate(reader, start=2):
        if len(row) != num_fields:
            raise ValueError(
                f"Row {row_number} has {len(row)} field(s), "
                f"but header has {num_fields} field(s)."
            )
        yield dict(zip(header, row))
