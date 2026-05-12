"""
A module for serializing dictionary records into various string formats.
"""

import csv
import io
import json
from typing import Any, Dict


def serialize_record(record: Dict[str, Any], format: str) -> str:
    """
    Serializes a dictionary record into a string based on the specified format.

    The supported formats are 'json', 'csv', and 'toml'.

    Args:
        record: The dictionary object to serialize.
        format: The target format string.

    Returns:
        A string representation of the record in the specified format.

    Raises:
        ValueError: If an unsupported format is provided.
        TypeError: If the record contains types incompatible with the 'toml'
                   format, which only supports primitives.
    """
    if format == 'json':
        # Per requirements, sort keys in JSON output.
        return json.dumps(record, sort_keys=True)

    if format == 'csv':
        # Per requirements, emit a header row and one data row.
        if not record:
            return ""

        # Use an in-memory stream to build the CSV string.
        string_io = io.StringIO()
        # Use lineterminator='\n' for consistent line endings.
        writer = csv.writer(string_io, lineterminator='\n')

        header = list(record.keys())
        data_row = list(record.values())

        writer.writerow(header)
        writer.writerow(data_row)

        return string_io.getvalue()

    if format == 'toml':
        # Per requirements, emit 'key = value' lines for primitive values.
        lines = []
        for key, value in record.items():
            if isinstance(value, str):
                # Use json.dumps for robust quoting and escaping of strings.
                formatted_value = json.dumps(value)
            elif isinstance(value, bool):
                # TOML booleans are lowercase.
                formatted_value = str(value).lower()
            elif isinstance(value, (int, float)):
                formatted_value = str(value)
            else:
                # Non-primitive types are not supported for this simple TOML format.
                raise TypeError(
                    "Unsupported value type for TOML serialization: "
                    f"{type(value).__name__}"
                )
            lines.append(f"{key} = {formatted_value}")
        return "\n".join(lines)

    raise ValueError(f"Unsupported serialization format: '{format}'")
