import csv
import io

REQUIRED_FIELDS = ("region", "product", "quantity", "cents")


def aggregate_sales(csv_text: str) -> list[dict]:
    if not isinstance(csv_text, str):
        raise TypeError("csv_text must be a string")

    reader = csv.reader(io.StringIO(csv_text), strict=True)
    header = _read_header(reader)
    if header is None:
        return []

    field_indexes = _field_indexes(header)
    if field_indexes is None:
        return []

    totals: dict[tuple[str, str], tuple[int, int]] = {}

    for row in _data_rows(reader):
        parsed_row = _parse_sales_row(row, len(header), field_indexes)
        if parsed_row is None:
            continue

        region, product, quantity, cents = parsed_row
        key = (region, product)
        old_quantity, old_cents = totals.get(key, (0, 0))
        totals[key] = (old_quantity + quantity, old_cents + cents)

    return [_result_row(key, totals[key]) for key in sorted(totals)]


def _read_header(reader: csv.reader) -> list[str] | None:
    try:
        return next(reader)
    except StopIteration:
        return None
    except csv.Error:
        return None


def _data_rows(reader: csv.reader):
    while True:
        try:
            yield next(reader)
        except StopIteration:
            return
        except csv.Error:
            continue


def _field_indexes(header: list[str]) -> dict[str, int] | None:
    if not all(field in header for field in REQUIRED_FIELDS):
        return None

    return {field: header.index(field) for field in REQUIRED_FIELDS}


def _parse_sales_row(
    row: list[str],
    expected_width: int,
    field_indexes: dict[str, int],
) -> tuple[str, str, int, int] | None:
    if len(row) != expected_width:
        return None

    quantity = _parse_integer(row[field_indexes["quantity"]])
    cents = _parse_integer(row[field_indexes["cents"]])
    if quantity is None or cents is None:
        return None

    region = row[field_indexes["region"]]
    product = row[field_indexes["product"]]
    return region, product, quantity, cents


def _parse_integer(text: str) -> int | None:
    stripped = text.strip()
    if not stripped:
        return None

    digits = stripped[1:] if stripped[0] in "+-" else stripped
    if not digits or not digits.isdecimal():
        return None

    return int(stripped)


def _result_row(key: tuple[str, str], totals: tuple[int, int]) -> dict:
    region, product = key
    quantity, cents = totals
    return {
        "region": region,
        "product": product,
        "quantity": quantity,
        "cents": cents,
    }
