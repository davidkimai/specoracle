def coerce_field(name, value, type_callable):
    try:
        return type_callable(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(name) from exc


def coerce_schema(raw: dict, schema: dict, nullable: set | None = None) -> dict:
    result = {}
    nullable = nullable or set()
    for name, (type_callable, default) in schema.items():
        if name in raw:
            value = raw[name]
            if name in nullable and value is None:
                result[name] = None
            else:
                result[name] = coerce_field(name, value, type_callable)
        else:
            result[name] = default
    return result
