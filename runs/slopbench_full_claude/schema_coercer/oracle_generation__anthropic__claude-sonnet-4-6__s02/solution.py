def coerce_schema(raw: dict, schema: dict) -> dict:
    result = {}
    for field, (type_callable, default) in schema.items():
        if field not in raw:
            result[field] = default
            continue
        try:
            result[field] = type_callable(raw[field])
        except (ValueError, TypeError) as exc:
            raise ValueError(field) from exc
    return result
