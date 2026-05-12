from collections.abc import Iterable, Iterator
import csv


def parse_csv_rows(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    """
    Parse CSV rows from an iterable of strings.

    The first non-empty CSV record is used as the header. Each subsequent
    non-empty record is yielded as a dictionary mapping header names to values.

    The input iterable is consumed lazily and is not materialized.
    """
    reader = csv.reader(lines)

    header: list[str] | None = None

    for row in reader:
        if not row:
            continue

        if header is None:
            header = row
            continue

        if len(row) != len(header):
            raise ValueError(
                f"CSV row has {len(row)} fields, but header has {len(header)} fields"
            )

        yield dict(zip(header, row))
