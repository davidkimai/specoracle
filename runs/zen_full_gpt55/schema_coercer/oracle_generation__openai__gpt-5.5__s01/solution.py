from collections.abc import Callable, Mapping
from typing import Any


def _require_mapping(value: Any, name: str) -> Mapping:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    return value


def _schema_pair(field: Any, entry: Any) -> tuple[Callable[[Any], Any], Any]:
    try:
        caster, default = entry
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"schema entry for field {field!r} must be a (callable, default) pair"
        ) from exc

    if not callable(caster):
        raise TypeError(f"schema caster for field {field!r} must be callable")

    return caster, default


def _coerce_field(field: Any, value: Any, caster: Callable[[Any], Any]) -> Any:
    try:
        return caster(value)
    except Exception as exc:
        raise ValueError(f"failed to coerce field {field!r}") from exc


def coerce_schema(raw: dict, schema: dict) -> dict:
    raw_mapping = _require_mapping(raw, "raw")
    schema_mapping = _require_mapping(schema, "schema")

    coerced = {}

    for field, entry in schema_mapping.items():
        caster, default = _schema_pair(field, entry)

        if field not in raw_mapping:
            coerced[field] = default
            continue

        coerced[field] = _coerce_field(field, raw_mapping[field], caster)

    return coerced
