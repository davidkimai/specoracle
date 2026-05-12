"""
A module for coercing a dictionary to a specified schema.
"""

from typing import Dict, Any, Tuple, Callable

def coerce_schema(raw: Dict[str, Any], schema: Dict[str, Tuple[Callable, Any]]) -> Dict[str, Any]:
    """
    Coerces a raw dictionary to conform to a given schema.

    For each field in the schema, this function attempts to find a corresponding
    value in the raw dictionary. If a value is found, it is cast using the
    provided type callable. If it is not found, the specified default value is
    used instead.

    Args:
        raw: The input dictionary with raw, untyped values.
        schema: A dictionary defining the desired output structure.
                Keys are the expected field names (str).
                Values are tuples of (type_callable, default_value), where
                `type_callable` is a function to cast the raw value (e.g., int),
                and `default_value` is the value to use if the field is
                missing from the raw dictionary.

    Returns:
        A new dictionary with fields and values conforming to the schema.

    Raises:
        ValueError: If a value from the raw dictionary cannot be cast to the
                    target type specified in the schema. The error message will
                    include the name of the field that failed the cast.
    """
    coerced_data = {}
    for field_name, (type_callable, default_value) in schema.items():
        if field_name in raw:
            raw_value = raw[field_name]
            try:
                coerced_value = type_callable(raw_value)
                coerced_data[field_name] = coerced_value
            except (ValueError, TypeError) as e:
                # Catch exceptions common during type casting (e.g., int('text'))
                # and raise a more specific error as required.
                raise ValueError(f"Failed to cast field '{field_name}'") from e
        else:
            coerced_data[field_name] = default_value
    return coerced_data
