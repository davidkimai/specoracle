"""A module for streaming parsing of CSV data."""

import csv
from typing import Dict, Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[Dict[str, str]]:
    """
    Parses an iterable of CSV lines into an iterator of dictionaries.

    This function processes the input in a streaming fashion, without loading the
    entire dataset into memory.

    The first non-empty line from the input is treated as the header row.
    Each subsequent non-empty line is treated as a data row. Empty lines or
    lines containing only whitespace are ignored.

    The CSV parsing handles quoted fields, so commas within quotes are
    correctly processed.

    Args:
        lines: An iterable of strings, where each string represents one line
               of CSV data.

    Yields:
        An iterator of dictionaries, where each dictionary represents a data
        row, mapping header names to their corresponding cell values. If the
        input contains no non-empty lines, the iterator will be empty.
    """
    # Create a generator that filters out empty or whitespace-only lines.
    # This preserves the streaming nature of the input.
    non_empty_lines = (line for line in lines if line and line.strip())

    # The csv.reader works with any iterator of strings.
    reader = csv.reader(non_empty_lines)

    try:
        # The first item from the reader is the header.
        header = next(reader)
    except StopIteration:
        # This occurs if the input `lines` is empty or contains only empty lines.
        # In this case, we yield nothing and simply return.
        return

    # The rest of the reader iterator contains the data rows.
    # We iterate through them and create dictionaries.
    for row in reader:
        # The zip function pairs header elements with row elements. If a row is
        # shorter than the header, the corresponding dictionary will have fewer
        # keys. If it's longer, the extra values are ignored.
        yield dict(zip(header, row))
