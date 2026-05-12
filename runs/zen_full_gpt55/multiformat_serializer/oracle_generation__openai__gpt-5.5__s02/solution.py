import csv
import io
import json
import math
import re
from typing import Any

_BARE_TOML_KEY = re.compile(r"^[A-Za-z0-9_-]+$")


def serialize_record(record: dict, format: str) -> str:
    _validate_record(record)
    _validate_format(format)
    _validate_string_keys(record)

    if format == "json":
        return _serialize_json(record)

    if format == "csv":
        return _serialize_csv(record)

    if format == "toml":
        return _serialize_toml(record)

    raise ValueError("format must be one of: 'json', 'csv', 'toml'")


def _validate_record(record: Any) -> None:
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")


def _validate_format(format: Any) -> None:
    if not isinstance(format, str):
        raise TypeError("format must be a str")


def _validate_string_keys(record: dict) -> None:
    for key in record:
        if not isinstance(key, str):
            raise TypeError("record keys must be strings")


def _serialize_json(record: dict) -> str:
    try:
        return json.dumps(record, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise type(error)(f"record is not JSON serializable: {error}") from error


def _serialize_csv(record: dict) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")

    writer.writerow(record.keys())
    writer.writerow(_csv_cell(value) for value in record.values())

    return output.getvalue()


def _csv_cell(value: Any) -> Any:
    if value is None:
        return ""

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("CSV float values must be finite")
        return value

    if isinstance(value, str):
        return value

    raise TypeError("CSV serialization supports only primitive cell values")


def _serialize_toml(record: dict) -> str:
    lines = []

    for key, value in record.items():
        lines.append(f"{_toml_key(key)} = {_toml_value(value)}")

    return "\n".join(lines)


def _toml_key(key: str) -> str:
    if _BARE_TOML_KEY.fullmatch(key):
        return key

    return _toml_string(key)


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("TOML float values must be finite")
        return repr(value)

    if isinstance(value, str):
        return _toml_string(value)

    raise TypeError("TOML serialization supports only str, bool, int, and finite float values")


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)
