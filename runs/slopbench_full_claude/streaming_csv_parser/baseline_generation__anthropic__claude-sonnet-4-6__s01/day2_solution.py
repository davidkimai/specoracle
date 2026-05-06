import csv


def parse_csv_rows(lines, normalize_header=None):
    """Parse CSV rows from an iterable of strings, yielding dicts keyed by header names.

    The first non-empty line is treated as the header row. Each subsequent
    non-empty line is yielded as a dict mapping header names to cell values.
    Streaming behavior is preserved: the input iterable is not materialized.

    Args:
        lines: An iterable of strings representing lines of a CSV file.
        normalize_header: An optional callable applied to each header cell before
            building row dictionaries. When None, header cells are used as-is.

    Yields:
        dict[str, str]: Dictionaries mapping header field names to row values.
    """

    def non_empty(iterable):
        for line in iterable:
            stripped = line.rstrip('\n').rstrip('\r')
            if stripped.strip():
                yield stripped

    filtered = non_empty(lines)

    # Read the header from the first non-empty line
    try:
        header_line = next(filtered)
    except StopIteration:
        return

    # Parse the header using csv.reader to handle quoted fields correctly
    raw_header = next(csv.reader([header_line]))

    # Apply normalization if provided
    if normalize_header is not None:
        header = [normalize_header(cell) for cell in raw_header]
    else:
        header = raw_header

    # Parse each subsequent non-empty line
    for line in filtered:
        row = next(csv.reader([line]))
        # Pad or trim row to match header length for robustness
        if len(row) < len(header):
            row = row + [''] * (len(header) - len(row))
        yield dict(zip(header, row))
