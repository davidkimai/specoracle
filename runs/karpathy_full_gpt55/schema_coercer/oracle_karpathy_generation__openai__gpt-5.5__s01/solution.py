def coerce_schema(raw: dict, schema: dict) -> dict:
    """Return a dict with schema fields coerced from raw or filled with defaults."""
    result = {}

    for field, (type_callable, default) in schema.items():
        if field in raw:
            try:
                result[field] = type_callable(raw[field])
            except Exception as exc:
                raise ValueError(field) from exc
        else:
            result[field] = default

    return result
