import csv
from collections.abc import Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    """
    Parse CSV rows from an iterable of strings.

    The first non-empty CSV record is treated as the header. Subsequent non-empty
    records are yielded as dictionaries mapping header names to cell values.

    Missing cells are represented as empty strings. Extra cells are ignored.
    """
    reader = csv.reader(lines)

    header: list[str] | None = None
    for record in reader:
        if record:
            header = record
            break

    if header is None:
        return

    for record in reader:
        if not record:
            continue

        yield {
            column_name: record[index] if index < len(record) else ""
            for index, column_name in enumerate(header)
        }
