import csv
import io
import json
import math
import re
from typing import Any


_TOML_BARE_KEY = re.compile(r"^[A-Za-z0-9_-]+$")


def serialize_record(record: dict, format: str) -> str:
    _validate_record(record)

    if not isinstance(format, str):
        raise TypeError("format must be a string")

    if format == "json":
        return _serialize_json(record)
    if format == "csv":
        return _serialize_csv(record)
    if format == "toml":
        return _serialize_toml(record)

    raise ValueError("unsupported format: expected 'json', 'csv', or 'toml'")


def _validate_record(record: dict) -> None:
    if not isinstance(record, dict):
        raise TypeError("record must be a dictionary")

    for key in record:
        if not isinstance(key, str):
            raise TypeError(f"record keys must be strings; got {type(key).__name__}")


def _serialize_json(record: dict) -> str:
    try:
        return json.dumps(record, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise TypeError(f"record is not JSON serializable: {error}") from error


def _serialize_csv(record: dict) -> str:
    _validate_csv_values(record)

    fieldnames = list(record.keys())
    row = [record[key] for key in fieldnames]

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(fieldnames)
    writer.writerow(row)
    return output.getvalue()


def _validate_csv_values(record: dict) -> None:
    for key, value in record.items():
        if _is_csv_cell(value):
            continue
        raise TypeError(
            f"CSV value for key {key!r} must be str, int, float, or bool; "
            f"got {type(value).__name__}"
        )


def _is_csv_cell(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) and value is not None


def _serialize_toml(record: dict) -> str:
    lines = []

    for key, value in record.items():
        toml_key = _format_toml_key(key)
        toml_value = _format_toml_value(key, value)
        lines.append(f"{toml_key} = {toml_value}")

    return "\n".join(lines)


def _format_toml_key(key: str) -> str:
    if _TOML_BARE_KEY.fullmatch(key):
        return key
    return json.dumps(key, ensure_ascii=False)


def _format_toml_value(key: str, value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"TOML float for key {key!r} must be finite")
        return repr(value)

    raise TypeError(
        f"TOML value for key {key!r} must be str, int, float, or bool; "
        f"got {type(value).__name__}"
    )
