"""
streaming_csv_parser.py

Streaming CSV parser that yields row dictionaries without buffering the input.
"""

import csv


def parse_csv_rows(lines):
    """
    Parse a streaming iterable of CSV lines into row dictionaries.

    The first non-empty line is treated as the header row. Each subsequent
    non-empty line is yielded as a dict mapping header names to cell values.

    Args:
        lines: An iterable of strings (may be a generator or any lazy source).

    Yields:
        dict[str, str]: Mapping of header field names to row cell values.

    Raises:
        ValueError: If the input contains no non-empty lines (no header found).
        ValueError: If a data row has a different number of fields than the header.
    """
    non_empty = (line for line in lines if line.strip())

    header = _read_header(non_empty)

    for row_fields in csv.reader(non_empty):
        if len(row_fields) != len(header):
            raise ValueError(
                f"Row has {len(row_fields)} field(s) but header has {len(header)}: {row_fields}"
            )
        yield dict(zip(header, row_fields))


def _read_header(non_empty_lines):
    """
    Consume and parse the first line from non_empty_lines as the CSV header.

    Args:
        non_empty_lines: An iterator of non-empty strings.

    Returns:
        list[str]: The parsed header field names.

    Raises:
        ValueError: If the iterator is exhausted before a header line is found.
    """
    first_line = next(non_empty_lines, None)
    if first_line is None:
        raise ValueError("Input contains no non-empty lines; cannot determine header.")

    header_rows = list(csv.reader([first_line]))
    return header_rows[0]
