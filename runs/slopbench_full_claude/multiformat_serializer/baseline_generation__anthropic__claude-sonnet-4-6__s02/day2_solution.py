"""
multiformat_serializer.py

Provides serialize_record(record: dict, format: str, schema_version: str | None = None) -> str.
Supported formats: 'json', 'csv', 'toml'.

Day 2: When schema_version is provided, it is included as a header field
("schema_version") before all other fields in all formats.
"""

import json
import csv
import io


def _build_record(record: dict, schema_version) -> dict:
    """Return a new ordered dict with schema_version prepended if provided."""
    if schema_version is not None:
        return {"schema_version": schema_version, **record}
    return record


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


def serialize_record(record: dict, format: str, schema_version: str | None = None) -> str:
    effective_record = _build_record(record, schema_version)
    fmt = format.lower().strip()
    if fmt == "json":
        return _serialize_json(effective_record)
    elif fmt == "csv":
        return _serialize_csv(effective_record)
    elif fmt == "toml":
        return _serialize_toml(effective_record)
    else:
        raise ValueError(f"Unsupported format: {format!r}. Choose from 'json', 'csv', 'toml'.")
