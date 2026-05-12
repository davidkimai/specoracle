# -*- coding: utf-8 -*-
"""
A module for serializing a dictionary record into various formats.
"""

import csv
import io
import json
from typing import Any, Callable, Dict, List


def _format_toml_value(value: Any) -> str:
    """
    Formats a Python value into a TOML-compatible string representation.

    Supports bool, int, float, and str.
    Raises TypeError for unsupported types.
    """
    if isinstance(value, bool):
        return str(value).lower()

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, str):
        # Use json.dumps for robust string quoting and escaping.
        return json.dumps(value)

    raise TypeError(f"Value of type {type(value).__name__} is not TOML-serializable.")


def _serialize_json(record: Dict[str, Any]) -> str:
    """Serializes a dictionary to a JSON string with sorted keys."""
    return json.dumps(record, sort_keys=True)


def _serialize_csv(record: Dict[str, Any]) -> str:
    """
    Serializes a dictionary to a CSV string with a header and one data row.
    """
    if not record:
        return ""

    # Sort keys to ensure consistent column order.
    sorted_keys = sorted(record.keys())

    # Use an in-memory text buffer to build the CSV string.
    string_io = io.StringIO(newline="")
    writer = csv.writer(string_io)

    writer.writerow(sorted_keys)

    row_values = [record[key] for key in sorted_keys]
    writer.writerow(row_values)

    return string_io.getvalue()


def _serialize_toml(record: Dict[str, Any]) -> str:
    """
    Serializes a dictionary to a simple TOML string.

    Handles primitive values only and expects string keys.
    Keys are always quoted for safety.
    """
    lines: List[str] = []

    if not all(isinstance(key, str) for key in record.keys()):
        raise TypeError("All keys in the record must be strings for TOML serialization.")

    for key in sorted(record.keys()):
        value = record[key]
        try:
            # Quoting the key makes it safe for all valid string keys.
            formatted_key = json.dumps(key)
            formatted_value = _format_toml_value(value)
            lines.append(f"{formatted_key} = {formatted_value}")
        except TypeError as e:
            # Re-raise with more context about which key failed.
            raise TypeError(f"Error serializing key '{key}': {e}") from e

    return "\n".join(lines)


# A dispatch table to map format names to serializer functions.
_SERIALIZERS: Dict[str, Callable[[Dict[str, Any]], str]] = {
    'json': _serialize_json,
    'csv': _serialize_csv,
    'toml': _serialize_toml,
}


def serialize_record(record: dict, format: str) -> str:
    """
    Serializes a dictionary record into a string based on the specified format.

    Args:
        record: The dictionary to serialize.
        format: The target format. Supported values are 'json', 'csv', 'toml'.
                The format name is case-insensitive.

    Returns:
        A string representation of the record in the requested format.

    Raises:
        TypeError: If 'record' is not a dict or 'format' is not a string.
        ValueError: If the specified format is unsupported.
        TypeError: If the record contains types incompatible with the format
                   (e.g., non-primitive values for 'toml').
    """
    if not isinstance(record, dict):
        raise TypeError("The 'record' argument must be a dictionary.")
    if not isinstance(format, str):
        raise TypeError("The 'format' argument must be a string.")

    serializer = _SERIALIZERS.get(format.lower())

    if serializer is None:
        supported_formats = ", ".join(sorted(_SERIALIZERS.keys()))
        raise ValueError(
            f"Unsupported format: '{format}'. "
            f"Supported formats are: {supported_formats}."
        )

    return serializer(record)
