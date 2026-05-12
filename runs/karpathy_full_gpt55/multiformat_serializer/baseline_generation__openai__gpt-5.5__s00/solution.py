import csv
import json
import math
from io import StringIO
from typing import Any

__all__ = ["serialize_record"]


def serialize_record(record: dict, format: str) -> str:
    """
    Serialize a flat record dictionary to JSON, CSV, or TOML.

    Supported formats:
      - "json": JSON object with sorted keys.
      - "csv": a header row followed by one data row.
      - "toml": one `key = value` line per primitive value.

    TOML values support str, bool, int, and float. Other TOML value types raise
    TypeError because this serializer is intentionally limited to primitives.
    """
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")
    if not isinstance(format, str):
        raise TypeError("format must be a str")

    if format == "json":
        return json.dumps(record, sort_keys=True)
    if format == "csv":
        return _serialize_csv(record)
    if format == "toml":
        return _serialize_toml(record)

    raise ValueError("unsupported format: expected 'json', 'csv', or 'toml'")


def _serialize_csv(record: dict) -> str:
    output = StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(list(record.keys()))
    writer.writerow(list(record.values()))
    return output.getvalue()


def _serialize_toml(record: dict) -> str:
    lines = []
    for key, value in record.items():
        lines.append(f"{_format_toml_key(key)} = {_format_toml_value(value)}")
    return "\n".join(lines)


def _format_toml_key(key: Any) -> str:
    key_text = str(key)
    if key_text and all(_is_toml_bare_key_char(ch) for ch in key_text):
        return key_text
    return _quote_toml_basic_string(key_text)


def _is_toml_bare_key_char(ch: str) -> bool:
    return (
        "A" <= ch <= "Z"
        or "a" <= ch <= "z"
        or "0" <= ch <= "9"
        or ch == "_"
        or ch == "-"
    )


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
        return _quote_toml_basic_string(value)

    raise TypeError(
        "TOML serialization supports only primitive values: str, bool, int, and float"
    )


def _quote_toml_basic_string(text: str) -> str:
    escaped = []

    for ch in text:
        codepoint = ord(ch)

        if ch == '"':
            escaped.append('\\"')
        elif ch == "\\":
            escaped.append("\\\\")
        elif ch == "\b":
            escaped.append("\\b")
        elif ch == "\t":
            escaped.append("\\t")
        elif ch == "\n":
            escaped.append("\\n")
        elif ch == "\f":
            escaped.append("\\f")
        elif ch == "\r":
            escaped.append("\\r")
        elif codepoint < 0x20 or codepoint == 0x7F:
            escaped.append(f"\\u{codepoint:04X}")
        elif 0xD800 <= codepoint <= 0xDFFF:
            raise ValueError("TOML strings cannot contain Unicode surrogate code points")
        else:
            escaped.append(ch)

    return '"' + "".join(escaped) + '"'
