# streaming_csv_parser.py
"""
A module for streaming parsing of CSV data.
"""

import csv
from typing import Iterable, Iterator, Dict, List

def parse_csv_rows(lines: Iterable[str]) -> Iterator[Dict[str, str]]:
    """
    Parses an iterable of CSV lines into an iterator of dictionaries.

    The function processes the input in a streaming fashion, without loading the
    entire dataset into memory. It identifies the first non-empty line as the
    header row and uses it to create key-value pairs for subsequent data rows.
    Empty or whitespace-only lines are ignored throughout the input.

    Assumptions:
    - The CSV data is comma-separated.
    - The `csv` module's default dialect is sufficient for parsing (e.g.,
      double-quotes are used for fields containing commas).

    Args:
        lines: An iterable of strings, where each string represents a line
               from a CSV source.

    Yields:
        An iterator of dictionaries, where each dictionary represents a data
        row, mapping header keys to their corresponding cell values. If the
        input iterable is empty or contains only a header, the iterator
        will be empty.
    """
    # Create a generator that filters out empty or whitespace-only lines.
    # This ensures that the first line seen by the CSV reader is the header,
    # and that blank lines between data rows are skipped.
    non_empty_lines = (line for line in lines if line and not line.isspace())

    # csv.DictReader is an iterator that reads the first line from its input
    # as the header and yields subsequent lines as dictionaries. This perfectly
    # matches the streaming requirement.
    reader = csv.DictReader(non_empty_lines)

    # Yield each parsed row from the DictReader. This preserves the lazy
    # evaluation and streaming behavior.
    yield from reader
