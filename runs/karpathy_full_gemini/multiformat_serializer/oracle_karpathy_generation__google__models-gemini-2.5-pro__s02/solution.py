import csv
import io
import json
from typing import Any, Dict


def serialize_record(record: Dict[str, Any], format: str) -> str:
    """
    Serializes a dictionary record into a string based on the specified format.

    Args:
        record: A dictionary representing the data record.
        format: The target format for serialization. Supported formats are
                'json', 'csv', and 'toml'.

    Returns:
        A string representation of the record in the specified format.

    Raises:
        ValueError: If an unsupported format is requested.
        TypeError: For 'toml' format, if the record contains non-primitive
                   values (i.e., not str, int, float, or bool).
    """
    if format == 'json':
        return json.dumps(record, sort_keys=True)
    elif format == 'csv':
        string_io = io.StringIO()
        writer = csv.writer(string_io)
        writer.writerow(record.keys())
        writer.writerow(record.values())
        return string_io.getvalue()
    elif format == 'toml':
        lines = []
        for key, value in record.items():
            if isinstance(value, str):
                # Escape backslashes and double quotes for TOML basic strings.
                processed_value = value.replace('\\', '\\\\').replace('"', '\\"')
                value_str = f'"{processed_value}"'
            elif isinstance(value, bool):
                # TOML booleans are lowercase.
                value_str = str(value).lower()
            elif isinstance(value, (int, float)):
                value_str = str(value)
            else:
                # Raise an error for unsupported types like lists, dicts, None.
                raise TypeError(
                    f"Unsupported value type for TOML serialization: "
                    f"{type(value).__name__}"
                )
            lines.append(f"{key} = {value_str}")
        return "\n".join(lines)
    else:
        raise ValueError(f"Unsupported format: '{format}'")
