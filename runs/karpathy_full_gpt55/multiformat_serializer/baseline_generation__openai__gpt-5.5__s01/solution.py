import csv
import io
import json
import math
import re
from typing import Any


_BARE_TOML_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def serialize_record(record: dict, format: str) -> str:
    """
    Serialize a single dictionary record as JSON, CSV, or TOML.

    Supported formats:
    - 'json': JSON object with keys sorted.
    - 'csv': CSV text containing one header row and one data row.
    - 'toml': TOML key/value lines for primitive values.
    """
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")
    if not isinstance(format, str):
        raise TypeError("format must be a str")

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
            f"{_format_toml_key(key)} = {_format_toml_value(value)}"
            for key, value in record.items()
        )

    raise ValueError("unsupported format: expected 'json', 'csv', or 'toml'")


def _format_toml_key(key: Any) -> str:
    if not isinstance(key, str):
        raise TypeError("TOML keys must be strings")

    if _BARE_TOML_KEY_RE.match(key):
        return key

    return _format_toml_string(key)


def _format_toml_value(value: Any) -> str:
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
        return _format_toml_string(value)

    raise TypeError(
        "TOML serialization supports only primitive string, integer, float, and boolean values"
    )


def _format_toml_string(value: str) -> str:
    escaped = []
    for char in value:
        code = ord(char)
        if char == "\\":
            escaped.append("\\\\")
        elif char == '"':
            escaped.append('\\"')
        elif char == "\b":
            escaped.append("\\b")
        elif char == "\t":
            escaped.append("\\t")
        elif char == "\n":
            escaped.append("\\n")
        elif char == "\f":
            escaped.append("\\f")
        elif char == "\r":
            escaped.append("\\r")
        elif code < 0x20 or code == 0x7F:
            escaped.append(f"\\u{code:04X}")
        else:
            escaped.append(char)
    return '"' + "".join(escaped) + '"'
