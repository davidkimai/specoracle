import csv
from typing import Dict, Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[Dict[str, str]]:
    """
    Parses a stream of CSV lines into an iterator of dictionaries.

    The first non-empty line from the input iterable is treated as the header.
    Each subsequent non-empty line is treated as a data row. Lines that are
    empty or contain only whitespace are ignored.

    This implementation is streaming and does not load the entire input into
    memory. It uses the standard library `csv` module for robust parsing.

    Args:
        lines: An iterable of strings, where each string represents a line
               in a CSV-like format.

    Yields:
        An iterator of dictionaries, where each dictionary maps header
        fieldnames to the corresponding values in a row. For example:
        {'header1': 'value1a', 'header2': 'value1b'}
    """
    # Create a generator that filters out lines that are empty or contain only
    # whitespace. This ensures that the first item seen by DictReader is the
    # intended header row.
    non_empty_lines = (line for line in lines if line.strip())

    # Use csv.DictReader for parsing. It is a streaming iterator that
    # automatically uses the first row from its input as the header.
    # `skipinitialspace=True` handles leading whitespace on fields,
    # e.g., " a, b" is parsed as fields "a" and "b".
    reader = csv.DictReader(non_empty_lines, skipinitialspace=True)

    yield from reader
