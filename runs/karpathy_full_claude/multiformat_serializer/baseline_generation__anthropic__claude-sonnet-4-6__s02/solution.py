"""
multiformat_serializer.py

Provides serialize_record(record: dict, format: str) -> str.
Supports 'json', 'csv', and 'toml' output formats.
"""

import json
import csv
import io


def _serialize_json(record: dict) -> str:
    """Serialize record to JSON with sorted keys."""
    return json.dumps(record, sort_keys=True)


def _serialize_csv(record: dict) -> str:
    """Serialize record to CSV with a header row and one data row."""
    output = io.StringIO()
    fieldnames = list(record.keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()
    writer.writerow(record)
    return output.getvalue()


def _toml_value(value) -> str:
    """Format a primitive value as a TOML value string."""
    if isinstance(value, bool):
        # bool must be checked before int because bool is a subclass of int
        return "true" if value else "false"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return repr(value)
    elif isinstance(value, str):
        # Escape backslashes and double quotes inside TOML basic strings
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    else:
        # For non-primitive types, fall back to quoted string representation
        escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'


def _serialize_toml(record: dict) -> str:
    """Serialize record to TOML key = value lines for primitive values."""
    lines = []
    for key, value in record.items():
        # Only emit primitive values (skip dicts, lists, etc. that require
        # TOML table/array syntax beyond the scope of this task)
        if isinstance(value, (bool, int, float, str)):
            toml_val = _toml_value(value)
            lines.append(f"{key} = {toml_val}")
    return "\n".join(lines)


def serialize_record(record: dict, format: str) -> str:
    """
    Serialize a dictionary record into the specified format.

    Parameters
    ----------
    record : dict
        The data record to serialize.
    format : str
        One of 'json', 'csv', or 'toml'.

    Returns
    -------
    str
        The serialized representation of the record.

    Raises
    ------
    ValueError
        If an unsupported format is specified.
    TypeError
        If record is not a dict.
    """
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dict, got {type(record).__name__}")

    fmt = format.lower().strip()

    if fmt == "json":
        return _serialize_json(record)
    elif fmt == "csv":
        return _serialize_csv(record)
    elif fmt == "toml":
        return _serialize_toml(record)
    else:
        raise ValueError(
            f"Unsupported format '{format}'. Supported formats: 'json', 'csv', 'toml'."
        )
