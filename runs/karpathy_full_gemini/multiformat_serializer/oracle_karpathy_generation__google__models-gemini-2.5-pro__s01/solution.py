# -*- coding: utf-8 -*-
"""
A module for serializing a dictionary record into multiple string formats.
"""

import csv
import io
import json
from typing import Dict

def serialize_record(record: Dict, format: str) -> str:
    """
    Serializes a dictionary record into a string based on the specified format.

    Args:
        record: The dictionary to serialize.
        format: The target format. Supported values are 'json', 'csv', 'toml'.

    Returns:
        A string representation of the record in the specified format.

    Raises:
        ValueError: If the format is not one of the supported values.
        TypeError: For 'toml' format, if a value in the record is not a
                   primitive type (str, bool, int, float).
    """
    if format == 'json':
        return json.dumps(record, sort_keys=True)

    if format == 'csv':
        string_io = io.StringIO()
        # Ensure a consistent, sorted order for columns.
        sorted_keys = sorted(record.keys())
        
        writer = csv.writer(string_io)
        writer.writerow(sorted_keys)
        writer.writerow([record[key] for key in sorted_keys])
        
        return string_io.getvalue()

    if format == 'toml':
        lines = []
        # Ensure a consistent, sorted order for keys.
        for key in sorted(record.keys()):
            value = record[key]
            
            if isinstance(value, str):
                # Use json.dumps to handle string quoting and escaping.
                formatted_value = json.dumps(value)
            elif isinstance(value, bool):
                # TOML booleans are lowercase.
                formatted_value = str(value).lower()
            elif isinstance(value, (int, float)):
                formatted_value = str(value)
            else:
                raise TypeError(
                    f"TOML serialization supports only primitive types "
                    f"(str, bool, int, float), but got type "
                    f"'{type(value).__name__}' for key '{key}'."
                )
            
            lines.append(f"{key} = {formatted_value}")
            
        return "\n".join(lines)

    raise ValueError(f"Unsupported format: '{format}'")
