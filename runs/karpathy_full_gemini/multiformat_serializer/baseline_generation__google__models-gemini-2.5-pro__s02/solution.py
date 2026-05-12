import csv
import io
import json
import re
from typing import Any, Dict

# According to TOML v1.0.0 spec, bare keys may only contain ASCII letters,
# ASCII digits, underscores, and dashes (A-Za-z0-9_-).
_TOML_BARE_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _serialize_json(record: Dict[str, Any]) -> str:
    """Serializes a dictionary to a JSON string with sorted keys."""
    return json.dumps(record, sort_keys=True)


def _serialize_csv(record: Dict[str, Any]) -> str:
    """Serializes a dictionary to a CSV string with a header and one data row."""
    if not record:
        return ""

    # Use io.StringIO to capture CSV output in a string.
    string_io = io.StringIO()
    writer = csv.writer(string_io)

    # In Python 3.7+, dicts preserve insertion order, so the order of keys
    # and values will be consistent.
    writer.writerow(record.keys())
    writer.writerow(record.values())

    return string_io.getvalue()


def _serialize_toml(record: Dict[str, Any]) -> str:
    """
    Serializes a dictionary to a simplified TOML string.

    This implementation supports only primitive value types (str, int, float, bool)
    and requires keys to be valid TOML bare keys (alphanumeric, _, -).
    """
    lines = []
    for key, value in record.items():
        if not _TOML_BARE_KEY_RE.match(key):
            raise ValueError(
                f"Invalid TOML key: '{key}'. Only ASCII letters, digits, "
                "underscores, and dashes are permitted."
            )

        if isinstance(value, str):
            # Escape backslashes and double quotes for TOML basic strings.
            escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
            formatted_value = f'"{escaped_value}"'
        elif isinstance(value, bool):
            # TOML booleans must be lowercase.
            formatted_value = str(value).lower()
        elif isinstance(value, (int, float)):
            formatted_value = str(value)
        else:
            raise TypeError(
                f"Value for key '{key}' has an unsupported type for TOML "
                f"serialization: {type(value).__name__}"
            )

        lines.append(f"{key} = {formatted_value}")

    return "\n".join(lines)


def serialize_record(record: Dict[str, Any], format: str) -> str:
    """
    Serializes a dictionary record into a string based on the specified format.

    Supports 'json', 'csv', and a simplified 'toml' format.

    Args:
        record: The dictionary object to serialize.
        format: The target format. Must be one of 'json', 'csv', or 'toml'.

    Returns:
        The serialized string representation of the record.

    Raises:
        ValueError: If an unsupported format is requested or if a key is
                    invalid for the specified format (e.g., TOML).
        TypeError: If a value's type is unsupported by the chosen format
                   (e.g., non-primitive types for TOML).
    """
    if format == 'json':
        return _serialize_json(record)
    elif format == 'csv':
        return _serialize_csv(record)
    elif format == 'toml':
        return _serialize_toml(record)
    else:
        raise ValueError(f"Unsupported serialization format: '{format}'")
