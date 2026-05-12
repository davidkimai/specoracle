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
        keys = list(record.keys())
        writer.writerow(keys)
        writer.writerow([record[key] for key in keys])
        return output.getvalue()

    if format == "toml":
        return "\n".join(
            f"{_toml_key(key)} = {_toml_value(value)}"
            for key, value in record.items()
        )

    raise ValueError("format must be 'json', 'csv', or 'toml'")


def _toml_key(key: Any) -> str:
    if not isinstance(key, str):
        raise TypeError("TOML keys must be strings")
    if _BARE_TOML_KEY.match(key):
        return key
    return json.dumps(key, ensure_ascii=False)


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    raise TypeError("TOML values must be primitive strings, integers, floats, or booleans")
