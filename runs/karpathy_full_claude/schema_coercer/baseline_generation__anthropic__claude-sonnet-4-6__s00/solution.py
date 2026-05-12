def coerce_schema(raw: dict, schema: dict) -> dict:
    result = {}
    for field, (type_callable, default) in schema.items():
        if field in raw:
            try:
                result[field] = type_callable(raw[field])
            except (ValueError, TypeError):
                raise ValueError(field)
        else:
            result[field] = default
    return result
