"""
multiformat_serializer.py

Serialize a flat dictionary to JSON, CSV, or TOML format.
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
        lines.append(f"{key} = {_to_toml_value(value)}")
    return "\n".join(lines)


_SERIALIZERS = {
    "json": _serialize_json,
    "csv": _serialize_csv,
    "toml": _serialize_toml,
}


def serialize_record(record: dict, format: str) -> str:
    """
    Serialize a flat dictionary to the requested format.

    Parameters
    ----------
    record : dict
        A flat dictionary with primitive values.
    format : str
        One of 'json', 'csv', or 'toml'.

    Returns
    -------
    str
        The serialized representation of the record.

    Raises
    ------
    ValueError
        If the format is not supported.
    TypeError
        If a value cannot be represented in the chosen format.
    """
    if not isinstance(record, dict):
        raise TypeError(f"record must be a dict, got {type(record).__name__!r}")

    serializer = _SERIALIZERS.get(format)
    if serializer is None:
        supported = ", ".join(sorted(_SERIALIZERS))
        raise ValueError(
            f"Unsupported format {format!r}. Supported formats: {supported}"
        )

    return serializer(record)
