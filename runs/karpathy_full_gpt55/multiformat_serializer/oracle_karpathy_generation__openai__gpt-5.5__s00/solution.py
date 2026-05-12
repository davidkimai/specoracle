import csv
import json
from io import StringIO


def serialize_record(record: dict, format: str) -> str:
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")

    if format == "json":
        return json.dumps(record, sort_keys=True)
    if format == "csv":
        return _serialize_csv(record)
    if format == "toml":
        return _serialize_toml(record)

    raise ValueError("format must be one of: json, csv, toml")


def _serialize_csv(record: dict) -> str:
    output = StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(record.keys())
    writer.writerow(record.values())
    return output.getvalue()


def _serialize_toml(record: dict) -> str:
    return "\n".join(
        f"{_toml_key(str(key))} = {_toml_value(value)}"
        for key, value in record.items()
    )


def _toml_key(key: str) -> str:
    if key and all(c.isalnum() or c in "_-" for c in key):
        return key
    return json.dumps(key)


def _toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    raise TypeError("TOML serialization supports only str, int, float, and bool values")
