"""
multiformat_serializer.py

Provides serialize_record(record: dict, format: str) -> str.
Supported formats: 'json', 'csv', 'toml'.
"""

import json
import csv
import io


def _serialize_json(record: dict) -> str:
    return json.dumps(record, sort_keys=True)


def _serialize_csv(record: dict) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(record.keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerow(record)
    return output.getvalue()


def _toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return repr(value)
    elif isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    else:
        escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'


def _serialize_toml(record: dict) -> str:
    lines = []
    for key, value in record.items():
        if isinstance(value, (bool, int, float, str)):
            lines.append(f"{key} = {_toml_value(value)}")
    return "\n".join(lines)


def serialize_record(record: dict, format: str) -> str:
    fmt = format.lower().strip()
    if fmt == "json":
        return _serialize_json(record)
    elif fmt == "csv":
        return _serialize_csv(record)
    elif fmt == "toml":
        return _serialize_toml(record)
    else:
        raise ValueError(f"Unsupported format: {format!r}. Choose from 'json', 'csv', 'toml'.")
