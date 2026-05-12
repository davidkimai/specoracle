#
# Karpathy Guidelines Compliance Statement
#
# 1. Think before coding:
#    - Assumptions:
#      - CSV column order is determined by the insertion order of keys in the input `record` dictionary.
#      - TOML keys are simple (valid as bare keys) and do not require quoting.
#      - TOML "primitive values" are defined as `str`, `int`, `float`, and `bool`.
#      - An empty `record` for CSV format should result in an empty string.
#      - The returned CSV string should not have a trailing newline.
#    - Design choice: A simple `if/elif/else` structure is used for format dispatching, as it's the most direct approach for a fixed set of three formats. Standard library modules (`json`, `csv`, `io`) are used to ensure correctness and avoid external dependencies.
#
# 2. Simplicity first:
#    - The implementation is contained within a single function as requested.
#    - No unnecessary abstractions (e.g., helper classes, format-specific functions) are introduced, as the logic for each format is straightforward and single-use.
#    - The code directly solves the specified requirements without adding extra features or configuration options. For TOML, it cleverly reuses `json.dumps` for string escaping to avoid reimplementing that logic.
#
# 3. Surgical changes:
#    - Not applicable, as this module is written from scratch.
#
# 4. Goal-driven execution:
#    - The function `serialize_record` has a clear, verifiable contract defined by its signature, docstring, and the functional requirements.
#    - Success criteria for each format:
#      - 'json': Returns a key-sorted JSON string. Verified by `json.dumps(..., sort_keys=True)`.
#      - 'csv': Returns a two-line string (header + row), with fields correctly quoted by the `csv` module. Verified by `csv.writer` logic.
#      - 'toml': Returns newline-separated `key = value` pairs for primitive types. Verified by type checking and string formatting logic.
#    - Edge cases like an empty dictionary for CSV and unsupported types for TOML are handled explicitly. Unsupported formats raise a `ValueError`.
#

import csv
import io
import json
from typing import Dict, Any

def serialize_record(record: Dict[str, Any], format: str) -> str:
    """
    Serializes a dictionary record into a string based on the specified format.

    Args:
        record: A dictionary representing the record to serialize.
        format: The target format ('json', 'csv', or 'toml').

    Returns:
        A string representation of the record in the specified format.

    Raises:
        ValueError: If the format is not one of 'json', 'csv', or 'toml'.
        TypeError: For 'toml' format, if a value in the record is not a
                   primitive type (str, int, float, bool).
    """
    if format == 'json':
        return json.dumps(record, sort_keys=True)

    elif format == 'csv':
        if not record:
            return ""

        string_io = io.StringIO()
        # Use default dialect (comma-separated, double-quote quoting)
        writer = csv.writer(string_io)

        writer.writerow(record.keys())
        writer.writerow(record.values())

        # Get the complete string and remove the final trailing newline
        return string_io.getvalue().strip()

    elif format == 'toml':
        lines = []
        for key, value in record.items():
            if isinstance(value, str):
                # Use json.dumps to correctly handle string quoting and escaping
                formatted_value = json.dumps(value)
            elif isinstance(value, bool):
                # TOML booleans are lowercase 'true' or 'false'
                formatted_value = str(value).lower()
            elif isinstance(value, (int, float)):
                formatted_value = str(value)
            else:
                raise TypeError(
                    f"Value of type {type(value).__name__} for key '{key}' "
                    "is not a primitive TOML value (str, int, float, bool)."
                )
            
            lines.append(f"{key} = {formatted_value}")
            
        return "\n".join(lines)

    else:
        raise ValueError(f"Unsupported format: '{format}'. Supported formats are 'json', 'csv', 'toml'.")
