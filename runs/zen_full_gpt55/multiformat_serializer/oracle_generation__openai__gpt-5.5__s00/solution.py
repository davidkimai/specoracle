import csv
import io
import json
import math
import re
from typing import Any

__all__ = ["serialize_record"]

_BARE_TOML_KEY = re.compile(r"^[A-Za-z0-9_-]+$")


def serialize_record(record: dict, format: str) -> str:
    _validate_record(record)
    _validate_format(format)

    if format == "json":
        return _serialize_json(record)

    if format == "csv":
        return _serialize_csv(record)

    if format == "toml":
        return _serialize_toml(record)

    raise ValueError("unsupported format: expected 'json', 'csv', or 'toml'")


def _validate_record(record: dict) -> None:
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")

    for key in record:
        if not isinstance(key, str):
            raise TypeError("record keys must be strings")


def _validate_format(format: str) -> None:
    if not isinstance(format, str):
        raise TypeError("format must be a string")


def _serialize_json(record: dict) -> str:
    try:
        return json.dumps(record, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError(f"record is not valid JSON data: {error}") from error


def _serialize_csv(record: dict) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")

    headers = list(record.keys())
    row = [_csv_cell(record[key]) for key in headers]

    writer.writerow(headers)
    writer.writerow(row)

    return output.getvalue()


def _csv_cell(value: Any) -> str:
    if isinstance(value, str):
        return value

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("CSV float values must be finite")
        return str(value)

    if value is None:
        return ""

    raise TypeError(f"unsupported CSV value type: {type(value).__name__}")


def _serialize_toml(record: dict) -> str:
    return "\n".join(
        f"{_toml_key(key)} = {_toml_value(value)}"
        for key, value in record.items()
    )


def _toml_key(key: str) -> str:
    if key and _BARE_TOML_KEY.fullmatch(key):
        return key

    return _toml_string(key)


def _toml_value(value: Any) -> str:
    if isinstance(value, str):
        return _toml_string(value)

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("TOML float values must be finite")
        return str(value)

    raise TypeError(f"unsupported TOML value type: {type(value).__name__}")


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)
