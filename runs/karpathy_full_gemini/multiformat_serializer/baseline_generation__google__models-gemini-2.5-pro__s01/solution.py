# -*- coding: utf-8 -*-
"""
A module for serializing a dictionary record into multiple string formats.
"""

import csv
import io
import json
from typing import Any, Dict


def _format_toml_value(value: Any) -> str:
    """
    Formats a Python primitive value into a TOML string representation.

    Args:
        value: The primitive value (str, bool, int, float) to format.

    Returns:
        A string suitable for a TOML value.

    Raises:
        TypeError: If the value is not a supported primitive type.
    """
    if isinstance(value, str):
        # TOML strings are quoted and require escaping of special characters.
        escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped_value}"'
    if isinstance(value, bool):
        # TOML booleans are lowercase 'true' or 'false'.
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)

    raise TypeError(
        f"Value of type '{type(value).__name__}' is not a primitive "
        "and cannot be serialized to simplified TOML."
    )


def _serialize_to_json(record: Dict[str, Any]) -> str:
    """
    Serializes a record to a JSON string with sorted keys.

    Args:
        record: The dictionary to serialize.

    Returns:
        A JSON formatted string.
    """
    return json.dumps(record, sort_keys=True)


def _serialize_to_csv(record: Dict[str, Any]) -> str:
    """
    Serializes a record to a CSV string with a header and one data row.

    The order of columns is determined by sorting the record keys alphabetically.

    Args:
        record: The dictionary to serialize.

    Returns:
        A CSV formatted string.
    """
    if not record:
        return ""

    string_io = io.StringIO()
    # Sort keys for a deterministic column order.
    sorted_keys = sorted(record.keys())

    # Use lineterminator='\n' for consistent line endings.
    writer = csv.writer(string_io, lineterminator='\n')
    writer.writerow(sorted_keys)
    writer.writerow([record[key] for key in sorted_keys])

    return string_io.getvalue()


def _serialize_to_toml(record: Dict[str, Any]) -> str:
    """
    Serializes a record to a simplified TOML string.

    This implementation handles primitive values only, emitting 'key = value'
    lines. The keys are sorted alphabetically for deterministic output.

    Args:
        record: The dictionary to serialize.

    Returns:
        A TOML formatted string.
    """
    lines = []
    # Sort keys for deterministic output.
    for key in sorted(record.keys()):
        value = record[key]
        formatted_value = _format_toml_value(value)
        lines.append(f"{key} = {formatted_value}")
    return "\n".join(lines)


def serialize_record(record: Dict[str, Any], format: str) -> str:
    """
    Serializes a dictionary record into a string based on the specified format.

    Args:
        record: A dictionary with primitive values.
        format: The target format, one of 'json', 'csv', or 'toml'.

    Returns:
        A string representation of the record in the specified format.

    Raises:
        ValueError: If the format is not supported.
        TypeError: If the record contains non-primitive values when
                   serializing to 'toml'.
    """
    if format == 'json':
        return _serialize_to_json(record)
    if format == 'csv':
        return _serialize_to_csv(record)
    if format == 'toml':
        return _serialize_to_toml(record)

    raise ValueError(
        f"Unsupported serialization format: '{format}'. "
        "Supported formats are 'json', 'csv', 'toml'."
    )
