"""
A module for streaming parsing of simple comma-separated value (CSV) data.
"""

import typing


def _parse_line(line: str) -> list[str]:
    """
    Parses a single line of a simple CSV.

    Splits the line by commas and strips leading/trailing whitespace from each
    resulting cell. This is a simple parser and does not handle quoted fields
    containing commas.

    Args:
        line: The string line to parse.

    Returns:
        A list of strings representing the cells in the line.
    """
    return [cell.strip() for cell in line.split(',')]


def parse_csv_rows(
    lines: typing.Iterable[str],
) -> typing.Iterator[dict[str, str]]:
    """
    Parses an iterable of CSV lines into an iterator of dictionaries.

    This function processes the input in a streaming fashion, without loading
    the entire dataset into memory.

    - The first non-empty line is treated as the header row.
    - Subsequent non-empty lines are treated as data rows.
    - Empty or whitespace-only lines are skipped.
    - Each yielded item is a dictionary mapping header names to row values.

    Args:
        lines: An iterable of strings, where each string is a line of CSV data.

    Yields:
        A dictionary for each data row.

    Raises:
        ValueError: If a data row has a different number of columns than
                    the header.
    """
    lines_iterator = iter(lines)
    header = []

    for line in lines_iterator:
        stripped_line = line.strip()
        if stripped_line:
            header = _parse_line(stripped_line)
            break
    else:
        # The iterable was exhausted without finding a non-empty line for a header.
        return

    num_columns = len(header)
    row_index = 0

    for line in lines_iterator:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        row_index += 1
        row_values = _parse_line(stripped_line)

        if len(row_values) != num_columns:
            raise ValueError(
                f"Row {row_index} has {len(row_values)} columns; "
                f"expected {num_columns}"
            )

        yield dict(zip(header, row_values))
