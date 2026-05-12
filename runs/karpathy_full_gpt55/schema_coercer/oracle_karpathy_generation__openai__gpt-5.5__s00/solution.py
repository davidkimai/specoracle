def coerce_schema(raw: dict, schema: dict) -> dict:
    result = {}

    for field, spec in schema.items():
        type_callable, default = spec

        if field not in raw:
            result[field] = default
            continue

        try:
            result[field] = type_callable(raw[field])
        except Exception as exc:
            raise ValueError(field) from exc

    return result
