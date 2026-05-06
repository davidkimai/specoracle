def coerce_schema(raw: dict, schema: dict, nullable: set | None = None) -> dict:
    result = {}
    nullable = nullable or set()
    for field, (type_callable, default) in schema.items():
        if field in raw:
            value = raw[field]
            if field in nullable and value is None:
                result[field] = None
            else:
                try:
                    result[field] = type_callable(value)
                except (ValueError, TypeError):
                    raise ValueError(field)
        else:
            result[field] = default
    return result
