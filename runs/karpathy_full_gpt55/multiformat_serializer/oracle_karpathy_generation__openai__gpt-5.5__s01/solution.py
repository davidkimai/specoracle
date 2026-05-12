import csv
import io
import json
import math
import re
from typing import Any


_BARE_TOML_KEY = re.compile(r"^[A-Za-z0-9_-]+$")


def serialize_record(record: dict, format: str) -> str:
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")

    if format == "json":
        return json.dumps(record, sort_keys=True)

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(record.keys())
        writer.writerow(record.values())
        return output.getvalue()

    if format == "toml":
        return "\n".join(
            f"{_toml_key(key)} = {_toml_value(value)}"
            for key, value in record.items()
        )

    raise ValueError("format must be one of: json, csv, toml")


def _toml_key(key: Any) -> str:
    key = str(key)
    if _BARE_TOML_KEY.match(key):
        return key
    return json.dumps(key)


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, str):
        return json.dumps(value)

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        return repr(value)

    raise TypeError("TOML serialization supports only str, bool, int, and float values")
