from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator


def parse_csv_rows(
    lines: Iterable[str],
    normalize_header: Callable[[str], str] | None = None,
) -> Iterator[dict[str, str]]:
    iterator = iter(lines)
    header: list[str] | None = None
    for raw in iterator:
        line = raw.strip()
        if not line:
            continue
        cells = [cell.strip() for cell in line.split(',')]
        if normalize_header is not None:
            cells = [normalize_header(cell) for cell in cells]
        header = cells
        break
    if header is None:
        return
    for raw in iterator:
        line = raw.strip()
        if not line:
            continue
        cells = [cell.strip() for cell in line.split(',')]
        yield dict(zip(header, cells))
