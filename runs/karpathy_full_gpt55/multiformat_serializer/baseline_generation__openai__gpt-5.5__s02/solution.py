import csv
import datetime
import io
import json
import math
import re
from typing import Any

__all__ = ["serialize_record"]

_BARE_TOML_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def serialize_record(record: dict, format: str) -> str:
    """Serialize a single record dictionary as JSON, CSV, or TOML."""
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")
    if not isinstance(format, str):
        raise TypeError("format must be a str")

    normalized_format = format.lower()

    if normalized_format == "json":
        return json.dumps(record, sort_keys=True)
    if normalized_format == "csv":
        return _serialize_csv(record)
    if normalized_format == "toml":
        return _serialize_toml(record)

    raise ValueError("unsupported format: expected 'json', 'csv', or 'toml'")


def _serialize_csv(record: dict) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(record.keys())
    writer.writerow(record.values())
    return output.getvalue()


def _serialize_toml(record: dict) -> str:
    lines = []
    for key, value in record.items():
        lines.append(f"{_format_toml_key(key)} = {_format_toml_value(value)}")
    return "\n".join(lines)


def _format_toml_key(key: Any) -> str:
    key_text = key if isinstance(key, str) else str(key)
    if _BARE_TOML_KEY_RE.fullmatch(key_text):
        return key_text
    return f'"{_escape_toml_basic_string(key_text)}"'


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
        return f'"{_escape_toml_basic_string(value)}"'

    if isinstance(value, datetime.datetime):
        return value.isoformat()

    if isinstance(value, datetime.date):
        return value.isoformat()

    if isinstance(value, datetime.time):
        if value.utcoffset() is not None:
            raise TypeError("TOML local time values cannot include a UTC offset")
        return value.isoformat()

    raise TypeError(f"unsupported TOML value type for primitive serialization: {type(value).__name__}")


def _escape_toml_basic_string(value: str) -> str:
    escaped = []

    for char in value:
        codepoint = ord(char)

        if 0xD800 <= codepoint <= 0xDFFF:
            raise ValueError("TOML strings cannot contain surrogate code points")

        if char == '"':
            escaped.append('\\"')
        elif char == "\\":
            escaped.append("\\\\")
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
        elif codepoint <= 0x1F or codepoint == 0x7F:
            escaped.append(f"\\u{codepoint:04X}")
        else:
            escaped.append(char)

    return "".join(escaped)
