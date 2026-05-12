from typing import Any, Callable, Dict, Tuple

__all__ = ["coerce_schema"]


def coerce_schema(raw: dict, schema: dict) -> dict:
    """
    Coerce values from raw according to schema.

    schema maps field names to (type_callable, default). For each schema field:
    - if the field exists in raw, raw[field] is passed to type_callable
    - if the field is missing, default is used as-is

    Raises:
        ValueError: with the field name when casting fails.
    """
    result: Dict[Any, Any] = {}

    for field, spec in schema.items():
        type_callable, default = spec

        if field in raw:
            try:
                result[field] = type_callable(raw[field])
            except Exception as exc:
                raise ValueError(field) from exc
        else:
            result[field] = default

    return result
