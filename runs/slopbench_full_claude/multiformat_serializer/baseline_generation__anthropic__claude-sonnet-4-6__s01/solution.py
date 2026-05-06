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
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\r\n")
    writer.writeheader()
    writer.writerow(record)
    return output.getvalue()


def _toml_format_value(value) -> str:
    """Format a primitive value for TOML output."""
    if isinstance(value, bool):
        # bool must be checked before int since bool is a subclass of int
        return "true" if value else "false"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return repr(value)
    elif isinstance(value, str):
        # Escape backslashes and double quotes within the string
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    else:
        # For any other primitive-like type, convert to string representation
        return f'"{str(value)}"'


def _serialize_toml(record: dict) -> str:
    """Serialize record to TOML key = value lines for primitive values."""
    lines = []
    for key, value in record.items():
        if isinstance(value, (bool, int, float, str)):
            formatted_value = _toml_format_value(value)
            lines.append(f"{key} = {formatted_value}")
        # Non-primitive values (dicts, lists, etc.) are skipped per requirements
    return "\n".join(lines)


def serialize_record(record: dict, format: str) -> str:
    """
    Serialize a record dictionary into the specified format string.

    Parameters
    ----------
    record : dict
        The data record to serialize.
    format : str
        The target format. Supported values: 'json', 'csv', 'toml'.

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
            f"Unsupported format: {format!r}. "
            "Supported formats are: 'json', 'csv', 'toml'."
        )
