import csv
import io

_REQUIRED_HEADERS = ("region", "product", "quantity", "cents")


def aggregate_sales(csv_text: str) -> list[dict]:
    if not isinstance(csv_text, str):
        raise TypeError("csv_text must be a string")

    reader = csv.reader(io.StringIO(csv_text), strict=True)
    header = _read_header(reader)
    if header is None:
        return []

    indices = _required_indices(header)
    if indices is None:
        return []

    totals: dict[tuple[str, str], tuple[int, int]] = {}

    for row in _read_rows(reader):
        parsed = _parse_row(row, header, indices)
        if parsed is None:
            continue

        region, product, quantity, cents = parsed
        key = (region, product)
        previous_quantity, previous_cents = totals.get(key, (0, 0))
        totals[key] = (previous_quantity + quantity, previous_cents + cents)

    return [
        {
            "region": region,
            "product": product,
            "quantity": quantity,
            "cents": cents,
        }
        for (region, product), (quantity, cents) in sorted(totals.items())
    ]


def _read_header(reader: csv.reader) -> list[str] | None:
    try:
        return next(reader)
    except (StopIteration, csv.Error):
        return None


def _read_rows(reader: csv.reader):
    while True:
        try:
            yield next(reader)
        except StopIteration:
            return
        except csv.Error:
            continue


def _required_indices(header: list[str]) -> dict[str, int] | None:
    indices: dict[str, int] = {}

    for name in _REQUIRED_HEADERS:
        if header.count(name) != 1:
            return None
        indices[name] = header.index(name)

    return indices


def _parse_row(
    row: list[str],
    header: list[str],
    indices: dict[str, int],
) -> tuple[str, str, int, int] | None:
    if len(row) != len(header):
        return None

    region = row[indices["region"]]
    product = row[indices["product"]]
    quantity_text = row[indices["quantity"]]
    cents_text = row[indices["cents"]]

    if not region or not product or not quantity_text or not cents_text:
        return None

    try:
        quantity = int(quantity_text)
        cents = int(cents_text)
    except ValueError:
        return None

    return region, product, quantity, cents
