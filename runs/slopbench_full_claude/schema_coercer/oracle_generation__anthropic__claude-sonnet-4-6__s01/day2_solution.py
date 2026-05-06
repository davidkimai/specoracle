def coerce_schema(raw: dict, schema: dict, nullable: set | None = None) -> dict:
    result = {}
    nullable = nullable or set()
    for field, (type_callable, default) in schema.items():
        if field not in raw:
            result[field] = default
            continue
        value = raw[field]
        if field in nullable and value is None:
            result[field] = None
            continue
        try:
            result[field] = type_callable(value)
        except (ValueError, TypeError) as exc:
            raise ValueError(field) from exc
    return result
