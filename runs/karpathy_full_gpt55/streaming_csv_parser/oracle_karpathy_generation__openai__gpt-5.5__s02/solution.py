import csv
from collections.abc import Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    """Yield CSV rows as dictionaries using the first non-empty line as header."""
    reader = csv.reader(line for line in lines if line.strip())

    try:
        header = next(reader)
    except StopIteration:
        return

    for row in reader:
        yield dict(zip(header, row))
