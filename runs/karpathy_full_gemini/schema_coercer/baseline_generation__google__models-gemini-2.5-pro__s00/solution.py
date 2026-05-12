# -*- coding: utf-8 -*-
"""
A module for coercing raw dictionary data into a typed structure based on a schema.
"""

from typing import Any, Callable, Dict, Tuple

__all__ = ["coerce_schema"]


def coerce_schema(
    raw: Dict[str, Any],
    schema: Dict[str, Tuple[Callable[[Any], Any], Any]],
) -> Dict[str, Any]:
    """
    Coerces a raw dictionary to a typed dictionary based on a schema.

    For each field defined in the schema, this function checks for its presence
    in the raw dictionary. If the field is present, its value is cast using the
    provided type callable. If the field is missing, the specified default
    value is used instead.

    Any fields present in the raw dictionary but not defined in the schema are
    ignored.

    Args:
        raw: The input dictionary containing raw, untyped values.
        schema: A dictionary that defines the desired output structure. It maps
                field names (str) to a tuple containing a type casting
                callable and a default value, i.e., (type_callable, default).

    Returns:
        A new dictionary with fields and values conforming to the schema.

    Raises:
        ValueError: If a value from the raw dictionary cannot be cast to the
                    target type specified for its field in the schema. The
                    error message will include the name of the failing field.
    """
    coerced_data = {}
    for field_name, (type_callable, default_value) in schema.items():
        if field_name in raw:
            raw_value = raw[field_name]
            try:
                coerced_value = type_callable(raw_value)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Failed to cast field '{field_name}'") from e
            coerced_data[field_name] = coerced_value
        else:
            coerced_data[field_name] = default_value
    return coerced_data
