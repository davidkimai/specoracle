def coerce_field(name, value, type_callable):
    try:
        return type_callable(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(name) from exc


def coerce_schema(raw: dict, schema: dict) -> dict:
    result = {}
    for name, (type_callable, default) in schema.items():
        if name in raw:
            result[name] = coerce_field(name, raw[name], type_callable)
        else:
            result[name] = default
    return result
