from __future__ import annotations

import csv
from collections.abc import Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    """
    Parse CSV rows from a streaming iterable of lines.

    The first non-empty CSV record is treated as the header. Each subsequent
    non-empty CSV record is yielded as a dictionary mapping header names to
    cell values.

    Raises:
        ValueError: If a row has a different number of cells than the header.
    """
    reader = csv.reader(lines)

    header: list[str] | None = None
    for row in reader:
        if row:
            header = row
            break

    if header is None:
        return

    for row in reader:
        if not row:
            continue

        if len(row) != len(header):
            raise ValueError(
                f"CSV row has {len(row)} cells, but header has {len(header)} columns"
            )

        yield dict(zip(header, row))
