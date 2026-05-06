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
    writer = csv.DictWriter(output, fieldnames=list(record.keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerow(record)
    return output.getvalue()


def _toml_value(value) -> str:
    """Convert a Python primitive value to its TOML string representation."""
    if isinstance(value, bool):
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
        # Fallback: represent as quoted string
        escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'


def _serialize_toml(record: dict) -> str:
    """Serialize record to TOML key = value lines for primitive values."""
    lines = []
    for key, value in record.items():
        if isinstance(value, (bool, int, float, str)):
            lines.append(f"{key} = {_toml_value(value)}")
    return "\n".join(lines)


def serialize_record(record: dict, format: str) -> str:
    """
    Serialize a dictionary record into the specified format string.

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
            f"Unsupported format: {format!r}. Must be one of 'json', 'csv', or 'toml'."
        )
