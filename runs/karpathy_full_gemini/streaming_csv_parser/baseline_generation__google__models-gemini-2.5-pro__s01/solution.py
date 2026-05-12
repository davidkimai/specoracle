import csv
import itertools
from typing import Iterable, Iterator, Dict

def parse_csv_rows(lines: Iterable[str]) -> Iterator[Dict[str, str]]:
    """
    Parses a stream of CSV lines into an iterator of dictionaries.

    The first non-empty line from the input is treated as the header.
    Subsequent non-empty lines are parsed as data rows. The function
    preserves the streaming nature of the input by not loading the entire
    set of lines into memory.

    This implementation uses the standard `csv` module to correctly handle
    CSV formatting complexities like quoted fields.

    Args:
        lines: An iterable of strings, where each string represents a line
               from a CSV source.

    Yields:
        An iterator of dictionaries, where each dictionary maps header
        fields to the corresponding values of a data row.
    """
    # Create an iterator that skips any initial empty or whitespace-only lines.
    # csv.DictReader requires that the first item it receives is the header.
    csv_stream = itertools.dropwhile(lambda line: not line.strip(), lines)

    # DictReader will consume the first line from the stream as the header.
    # If the stream is empty, the reader will also be empty, and the loop
    # below will not execute, which is the correct behavior.
    # The `skipinitialspace=True` argument handles whitespace after delimiters.
    reader = csv.DictReader(csv_stream, skipinitialspace=True)

    # The csv.reader (used internally by DictReader) can yield an empty list
    # for an empty line, which results in an empty dictionary from DictReader.
    # The requirement is to process non-empty lines, so we filter out these
    # empty dictionaries. An empty dictionary evaluates to False in a boolean
    # context.
    for row in reader:
        if row:
            yield row
