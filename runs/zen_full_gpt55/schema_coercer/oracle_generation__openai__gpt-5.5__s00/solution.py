from typing import Any, Callable, Tuple


def _parse_schema_entry(field_name: Any, entry: Any) -> Tuple[Callable[[Any], Any], Any]:
    if not isinstance(entry, tuple) or len(entry) != 2:
        raise ValueError(
            f"schema entry for field {field_name!r} must be a "
            "(type_callable, default) tuple"
        )

    type_callable, default = entry
    if not callable(type_callable):
        raise TypeError(f"type callable for field {field_name!r} must be callable")

    return type_callable, default


def _coerce_field(field_name: Any, type_callable: Callable[[Any], Any], value: Any) -> Any:
    try:
        return type_callable(value)
    except Exception as error:
        raise ValueError(f"failed to coerce field {field_name!r}") from error


def coerce_schema(raw: dict, schema: dict) -> dict:
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")
    if not isinstance(schema, dict):
        raise TypeError("schema must be a dict")

    coerced = {}

    for field_name, entry in schema.items():
        type_callable, default = _parse_schema_entry(field_name, entry)

        if field_name not in raw:
            coerced[field_name] = default
            continue

        coerced[field_name] = _coerce_field(field_name, type_callable, raw[field_name])

    return coerced
