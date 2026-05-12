from typing import Dict, Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[Dict[str, str]]:
    """
    Parses an iterable of CSV lines into an iterator of dictionaries.

    This function processes lines in a streaming fashion, without loading the
    entire dataset into memory. It assumes a simple CSV format where fields
    are separated by commas and do not contain commas themselves.

    The first non-empty line from the input is treated as the header row.
    Column names are determined from this line. Any leading or trailing
    whitespace around column names and data values is stripped.

    Subsequent non-empty lines are treated as data rows. Each data row is
    converted into a dictionary where keys are the header column names and
    values are the corresponding cell values from the row.

    Empty lines (or lines containing only whitespace) are ignored throughout
    the input.

    If a data row has a different number of columns than the header, the
    resulting dictionary will be formed by pairing header names and values
    up to the length of the shorter of the two. Extra values or headers
    are ignored, as per the behavior of `zip`.

    Args:
        lines: An iterable of strings, where each string represents one line
               of the CSV data.

    Yields:
        An iterator of dictionaries, with each dictionary representing a
        parsed data row. If no header is found (e.g., the input is empty),
        the iterator will be empty.
    """
    line_iterator = iter(lines)

    # Find the first non-empty line and treat it as the header.
    header_fields = None
    for line in line_iterator:
        stripped_line = line.strip()
        if stripped_line:
            header_fields = [h.strip() for h in stripped_line.split(',')]
            break

    # If no non-empty lines were found, there's no header and no data.
    if header_fields is None:
        return

    # Process the remaining lines as data rows.
    for line in line_iterator:
        stripped_line = line.strip()
        if stripped_line:
            values = [v.strip() for v in stripped_line.split(',')]
            yield dict(zip(header_fields, values))
