"""
A module for serializing a single data record into various formats.
"""

import csv
import io
import json
from typing import Any, Callable, Dict

#
# Private helper functions for TOML serialization
#

def _escape_toml_string(value: str) -> str:
    """Escapes a string for use in a TOML basic string."""
    escaped = value.replace('\\', '\\\\')
    escaped = escaped.replace('"', '\\"')
    escaped = escaped.replace('\b', '\\b')
    escaped = escaped.replace('\t', '\\t')
    escaped = escaped.replace('\n', '\\n')
    escaped = escaped.replace('\f', '\\f')
    escaped = escaped.replace('\r', '\\r')
    return escaped


def _format_toml_value(value: Any) -> str:
    """Formats a Python primitive value into its TOML string representation."""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return f'"{_escape_toml_string(value)}"'

    raise TypeError(
        f"Unsupported value type for TOML serialization: {type(value).__name__}"
    )

#
# Private serializer implementations for each format
#

def _serialize_json(record: Dict[str, Any]) -> str:
    """Serializes a record to a JSON string with sorted keys."""
    return json.dumps(record, sort_keys=True)


def _serialize_csv(record: Dict[str, Any]) -> str:
    """Serializes a record to a CSV string with a header and one data row."""
    if not record:
        return ""

    string_io = io.StringIO(newline='')
    writer = csv.writer(string_io)

    header = list(record.keys())
    row = list(record.values())

    writer.writerow(header)
    writer.writerow(row)

    return string_io.getvalue()


def _serialize_toml(record: Dict[str, Any]) -> str:
    """Serializes a record to a simplified TOML string."""
    lines = [
        f"{key} = {_format_toml_value(value)}"
        for key, value in record.items()
    ]
    return "\n".join(lines)


#
# Dispatcher mapping format names to serializer functions
#

_SERIALIZERS: Dict[str, Callable[[Dict[str, Any]], str]] = {
    'json': _serialize_json,
    'csv': _serialize_csv,
    'toml': _serialize_toml,
}


def serialize_record(record: Dict[str, Any], format: str) -> str:
    """
    Serializes a dictionary record into a string based on the specified format.

    Args:
        record: A dictionary representing the data record.
        format: A string specifying the output format ('json', 'csv', or 'toml').

    Returns:
        A string representation of the record in the requested format.

    Raises:
        TypeError: If 'record' is not a dict or 'format' is not a string.
        ValueError: If the specified format is not supported.
    """
    if not isinstance(record, dict):
        raise TypeError(
            f"Expected 'record' to be a dict, but got {type(record).__name__}"
        )
    if not isinstance(format, str):
        raise TypeError(
            f"Expected 'format' to be a str, but got {type(format).__name__}"
        )

    serializer = _SERIALIZERS.get(format.lower())

    if serializer is None:
        supported_formats = ", ".join(sorted(_SERIALIZERS.keys()))
        raise ValueError(
            f"Unsupported format: '{format}'. "
            f"Supported formats are: {supported_formats}."
        )

    return serializer(record)
