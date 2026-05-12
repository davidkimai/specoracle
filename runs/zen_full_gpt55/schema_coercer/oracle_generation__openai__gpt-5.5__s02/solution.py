"""Schema coercion helpers."""


def _require_dict(value, name):
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")


def _unpack_field_spec(field_name, spec):
    try:
        type_callable, default = spec
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"schema for field {field_name!r} must be a (type_callable, default) pair"
        ) from exc

    if not callable(type_callable):
        raise TypeError(f"schema for field {field_name!r} has a non-callable type")

    return type_callable, default


def _cast_field(field_name, type_callable, value):
    try:
        return type_callable(value)
    except Exception as exc:
        raise ValueError(f"failed to cast field {field_name!r}") from exc


def coerce_schema(raw: dict, schema: dict) -> dict:
    """Return a new dict containing schema fields coerced from raw or filled by defaults."""
    _require_dict(raw, "raw")
    _require_dict(schema, "schema")

    coerced = {}

    for field_name, spec in schema.items():
        type_callable, default = _unpack_field_spec(field_name, spec)

        if field_name in raw:
            coerced[field_name] = _cast_field(field_name, type_callable, raw[field_name])
            continue

        coerced[field_name] = default

    return coerced
