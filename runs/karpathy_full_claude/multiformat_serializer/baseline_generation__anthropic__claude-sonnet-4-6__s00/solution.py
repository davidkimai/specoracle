"""
multiformat_serializer.py

Provides serialize_record(record: dict, format: str) -> str
Supports 'json', 'csv', and 'toml' output formats.
"""

import json
import csv
import io


def _serialize_json(record: dict) -> str:
    """Serialize record to JSON with sorted keys."""
    return json.dumps(record, sort_keys=True)


def _serialize_csv(record: dict) -> str:
    """Serialize record to CSV with header and one data row."""
    output = io.StringIO()
    fieldnames = list(record.keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()
    writer.writerow(record)
    return output.getvalue()


def _toml_value(value) -> str:
    """Convert a primitive Python value to its TOML representation."""
    if isinstance(value, bool):
        # bool check must come before int since bool is subclass of int
        return "true" if value else "false"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return repr(value)
    elif isinstance(value, str):
        # Escape backslashes and double quotes
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    else:
        raise ValueError(
            f"Unsupported type for TOML primitive serialization: {type(value).__name__}"
        )


def _serialize_toml(record: dict) -> str:
    """Serialize record to TOML key = value lines for primitive values."""
    lines = []
    for key, value in record.items():
        toml_val = _toml_value(value)
        lines.append(f"{key} = {toml_val}")
    return "\n".join(lines)


def serialize_record(record: dict, format: str) -> str:
    """
    Serialize a dictionary record into the specified format.

    Parameters
    ----------
    record : dict
        The data record to serialize. Values must be primitives for TOML format.
    format : str
        One of 'json', 'csv', or 'toml'.

    Returns
    -------
    str
        The serialized string representation of the record.

    Raises
    ------
    ValueError
        If an unsupported format is specified.
    """
    fmt = format.lower().strip()

    if fmt == "json":
        return _serialize_json(record)
    elif fmt == "csv":
        return _serialize_csv(record)
    elif fmt == "toml":
        return _serialize_toml(record)
    else:
        raise ValueError(
            f"Unsupported format: '{format}'. Choose from 'json', 'csv', or 'toml'."
        )
