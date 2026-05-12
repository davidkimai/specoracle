import csv


def parse_csv_rows(lines):
    """Parse CSV rows from an iterable of strings, yielding dicts keyed by header names.

    The first non-empty line is treated as the comma-separated header row.
    Each subsequent non-empty line is yielded as a dict mapping header names to cell values.
    Streaming behavior is preserved: the input iterable is not converted to a list.

    Args:
        lines: An iterable of strings representing lines of a CSV file.

    Yields:
        dict[str, str]: Dictionaries mapping header names to cell values.
    """
    filtered = (line for line in lines if line.strip())
    reader = csv.DictReader(filtered)
    yield from reader
