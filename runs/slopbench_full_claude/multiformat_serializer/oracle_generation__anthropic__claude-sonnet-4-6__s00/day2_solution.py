"""
multiformat_serializer.py

Serialize a flat dictionary record into JSON, CSV, or TOML format.
"""

import json
import csv
import io


def _serialize_json(record: dict) -> str:
    return json.dumps(record, sort_keys=True)


def _serialize_csv(record: dict) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(record.keys()))
    writer.writeheader()
    writer.writerow(record)
    return output.getvalue()


def _to_toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    raise TypeError(f"Unsupported TOML value type: {type(value).__name__!r}")


def _serialize_toml(record: dict) -> str:
    lines = []
    for key, value in record.items():
        toml_value = _to_toml_value(value)
        lines.append(f"{key} = {toml_value}")
    return "\n".join(lines)


_SERIALIZERS = {
    "json": _serialize_json,
    "csv": _serialize_csv,
    "toml": _serialize_toml,
}


def _prepend_schema_version(record: dict, schema_version: str) -> dict:
    """Return a new dict with schema_version inserted before other fields."""
    result = {"schema_version": schema_version}
    result.update(record)
    return result


def serialize_record(record: dict, format: str, schema_version: str | None = None) -> str:
    """Serialize a flat dictionary record to the specified format string.

    Args:
        record: A flat dictionary with primitive values.
        format: One of 'json', 'csv', or 'toml'.
        schema_version: Optional version string. When provided, it is included
            as the first field ('schema_version') in the output.

    Returns:
        A string representation of the record in the requested format.

    Raises:
        ValueError: If the format is not supported.
        TypeError: If a value cannot be represented in the chosen format.
    """
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dict, got {type(record).__name__!r}")

    serializer = _SERIALIZERS.get(format)
    if serializer is None:
        supported = ", ".join(sorted(_SERIALIZERS))
        raise ValueError(
            f"Unsupported format {format!r}. Supported formats: {supported}"
        )

    if schema_version is not None:
        record = _prepend_schema_version(record, schema_version)

    return serializer(record)
