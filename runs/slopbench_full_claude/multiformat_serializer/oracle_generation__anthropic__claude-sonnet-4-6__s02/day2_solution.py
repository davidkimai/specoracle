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
    if isinstance(value, int) or isinstance(value, float):
        return str(value)
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
    """Serialize a flat dictionary record to the requested format string.

    Parameters
    ----------
    record:
        A flat dictionary whose values are primitive types.
    format:
        One of 'json', 'csv', or 'toml'.
    schema_version:
        Optional version string. When provided, it is included as the first
        field (``schema_version``) in the serialized output across all formats.

    Returns
    -------
    str
        The serialized representation of the record.

    Raises
    ------
    ValueError
        If the format is not supported.
    TypeError
        If the record is not a dict, or a value is not serializable in the
        requested format.
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
