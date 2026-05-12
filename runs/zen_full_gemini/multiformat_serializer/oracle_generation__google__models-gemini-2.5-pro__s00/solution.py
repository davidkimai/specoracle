# -*- coding: utf-8 -*-
"""
A module for serializing a dictionary record into various string formats.
"""

import csv
import io
import json
from typing import Any, Dict


def _serialize_json(record: Dict[str, Any]) -> str:
    """
    Serializes a dictionary to a JSON string with sorted keys.

    Args:
        record: The dictionary to serialize.

    Returns:
        A JSON formatted string.
    """
    return json.dumps(record, sort_keys=True)


def _serialize_csv(record: Dict[str, Any]) -> str:
    """
    Serializes a dictionary to a CSV string with a header and one data row.

    The columns are sorted alphabetically by key.

    Args:
        record: The dictionary to serialize.

    Returns:
        A CSV formatted string with a header row.
    """
    string_buffer = io.StringIO()
    # Use lineterminator='\n' for consistent output across platforms.
    writer = csv.writer(string_buffer, lineterminator='\n')

    sorted_keys = sorted(record.keys())
    values = [record[key] for key in sorted_keys]

    writer.writerow(sorted_keys)
    writer.writerow(values)

    return string_buffer.getvalue()


def _format_toml_value(value: Any) -> str:
    """
    Formats a Python primitive value for a simple TOML representation.

    Args:
        value: The value to format.

    Returns:
        A string representation suitable for a TOML value.

    Raises:
        TypeError: If the value is not a supported primitive type.
    """
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # json.dumps provides correct quoting and escaping for TOML basic strings.
        return json.dumps(value)

    raise TypeError(
        f"Value of type {type(value).__name__} is not a primitive and cannot be "
        "serialized to simple TOML."
    )


def _serialize_toml(record: Dict[str, Any]) -> str:
    """
    Serializes a dictionary with primitive values to a simple TOML string.

    Keys are sorted alphabetically. Each key-value pair is on a new line.

    Args:
        record: The dictionary to serialize.

    Returns:
        A simple TOML formatted string.

    Raises:
        TypeError: If any value in the record is not a primitive type.
    """
    lines = []
    for key in sorted(record.keys()):
        value = record[key]
        try:
            formatted_value = _format_toml_value(value)
            lines.append(f"{key} = {formatted_value}")
        except TypeError as e:
            # Add context to the error message about which key failed.
            raise TypeError(f"Error serializing key '{key}': {e}") from e

    return "\n".join(lines)


_SERIALIZERS = {
    'json': _serialize_json,
    'csv': _serialize_csv,
    'toml': _serialize_toml,
}


def serialize_record(record: Dict[str, Any], format: str) -> str:
    """
    Serializes a dictionary record into a string based on the specified format.

    Supported formats are 'json', 'csv', and 'toml'.

    - JSON output has sorted keys.
    - CSV output includes a header row with sorted keys, followed by a data row.
    - TOML output consists of 'key = value' lines for primitive values, with
      keys sorted alphabetically.

    Args:
        record: The dictionary to serialize.
        format: The target format ('json', 'csv', or 'toml').

    Returns:
        A string representation of the record in the chosen format.

    Raises:
        TypeError: If the 'record' argument is not a dictionary or if a value
                   in the record is incompatible with the chosen format (e.g.,
                   non-primitive for TOML).
        ValueError: If the 'format' is not one of the supported formats.
    """
    if not isinstance(record, dict):
        raise TypeError("The 'record' argument must be a dictionary.")

    serializer = _SERIALIZERS.get(format)

    if serializer is None:
        supported_formats = ", ".join(sorted(_SERIALIZERS.keys()))
        raise ValueError(
            f"Unsupported format: '{format}'. "
            f"Supported formats are: {supported_formats}."
        )

    return serializer(record)
