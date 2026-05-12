"""
A module for coercing a dictionary to a specified schema.
"""

from typing import Any, Callable, Dict, Tuple


def coerce_schema(raw: Dict[str, Any], schema: Dict[str, Tuple[Callable[[Any], Any], Any]]) -> Dict[str, Any]:
    """
    Coerces a raw dictionary to conform to a given schema.

    For each field in the schema, this function attempts to find it in the raw
    dictionary. If found, the value is cast using the specified type callable.
    If not found, the default value from the schema is used.

    Args:
        raw: A dictionary of raw data with string keys.
        schema: A dictionary defining the target schema. Each key is a field
                name, and each value is a tuple containing a type callable
                (e.g., int, str) and a default value.

    Returns:
        A new dictionary with fields and values conforming to the schema.

    Raises:
        ValueError: If a value from the raw dictionary cannot be cast to the
                    specified type, with a message indicating the problematic field.
    """
    coerced_data = {}
    for field_name, (type_callable, default) in schema.items():
        if field_name in raw:
            raw_value = raw[field_name]
            try:
                coerced_data[field_name] = type_callable(raw_value)
            except (ValueError, TypeError) as e:
                # Catch exceptions common during type casting (e.g., int('a')).
                raise ValueError(f"Failed to cast field '{field_name}'") from e
        else:
            coerced_data[field_name] = default
    return coerced_data
