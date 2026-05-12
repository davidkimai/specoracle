"""Utilities for coercing dictionaries according to a simple schema."""

from typing import Any, Callable, Dict, Mapping, Tuple

Schema = Mapping[str, Tuple[Callable[[Any], Any], Any]]


def coerce_schema(raw: dict, schema: dict) -> dict:
    """
    Coerce values from ``raw`` according to ``schema``.

    ``schema`` maps field names to ``(type_callable, default)`` pairs. For each
    field in the schema, if the field exists in ``raw``, its value is passed to
    the callable. If the field is missing, the default is used as-is.

    Raises:
        ValueError: If coercion for a present field fails. The field name is
        included as the ValueError message.
    """
    result: Dict[str, Any] = {}

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


__all__ = ["coerce_schema"]
