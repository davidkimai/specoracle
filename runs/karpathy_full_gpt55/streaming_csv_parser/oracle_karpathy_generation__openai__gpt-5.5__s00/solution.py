import csv
from collections.abc import Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    reader = csv.reader(lines)

    header = None
    for row in reader:
        if row:
            header = row
            break

    if header is None:
        return

    for row in reader:
        if not row:
            continue
        yield {name: row[i] if i < len(row) else "" for i, name in enumerate(header)}
