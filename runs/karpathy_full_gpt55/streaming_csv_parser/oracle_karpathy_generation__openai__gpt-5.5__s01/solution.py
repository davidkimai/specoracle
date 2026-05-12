import csv
from collections.abc import Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    reader = csv.reader(lines)
    header = None

    for row in reader:
        if not row:
            continue

        if header is None:
            header = row
            continue

        yield dict(zip(header, row))
