"""Schema coercion utility.

Assumptions:
- schema entries are valid two-item ``(type_callable, default)`` pairs.
- output contains only fields declared in schema.
- defaults are used as provided; they are not cast or copied.
"""


def coerce_schema(raw: dict, schema: dict) -> dict:
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
