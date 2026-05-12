import csv


def parse_csv_rows(lines):
    """Parse CSV rows from an iterable of strings, yielding dicts keyed by header names.

    The first non-empty line is treated as the header row. Each subsequent
    non-empty line is yielded as a dict mapping header names to cell values.
    Streaming behavior is preserved: the input iterable is not converted to a list.

    Args:
        lines: An iterable of strings representing lines of CSV data.

    Yields:
        dict[str, str]: A dictionary mapping header field names to row cell values.
    """
    def non_empty(iterable):
        for line in iterable:
            stripped = line.rstrip('\n').rstrip('\r')
            if stripped.strip():
                yield stripped

    filtered = non_empty(lines)
    reader = csv.DictReader(filtered)
    # csv.DictReader reads the first row as fieldnames automatically when
    # fieldnames is not provided. We need to supply it ourselves to keep
    # streaming behavior and handle the first non-empty line as the header.

    # Get the header line manually from the filtered iterator
    # We need to reconstruct because DictReader would consume from filtered.
    # Re-implement using csv.reader for full control.
    pass


def parse_csv_rows(lines):  # noqa: F811  (redefinition for clarity)
    """Parse CSV rows from an iterable of strings, yielding dicts keyed by header names.

    The first non-empty line is treated as the header row. Each subsequent
    non-empty line is yielded as a dict mapping header names to cell values.
    Streaming behavior is preserved: the input iterable is not converted to a list.

    Args:
        lines: An iterable of strings representing lines of CSV data.

    Yields:
        dict[str, str]: A dictionary mapping header field names to row cell values.
    """
    def non_empty_lines(iterable):
        """Yield only non-empty lines, stripping trailing newline characters."""
        for line in iterable:
            # Strip common line endings but preserve internal whitespace
            stripped = line.rstrip('\r\n')
            if stripped.strip():  # skip blank/whitespace-only lines
                yield stripped

    filtered = non_empty_lines(lines)
    reader = csv.reader(filtered)

    # Read the header row (first non-empty line)
    try:
        headers = next(reader)
    except StopIteration:
        return  # No data at all; yield nothing

    # Yield a dict for each subsequent non-empty line
    for row in reader:
        # If the row has fewer fields than headers, fill missing with empty string
        # If more fields, extras are ignored (consistent with csv.DictReader default)
        row_dict = {}
        for i, header in enumerate(headers):
            row_dict[header] = row[i] if i < len(row) else ''
        yield row_dict
