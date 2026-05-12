"""
A module for coercing dictionary data based on a schema.
"""

def coerce_schema(raw: dict, schema: dict) -> dict:
    """
    Coerces a raw dictionary to a typed dictionary based on a schema.

    For each field in the schema, this function checks if the field exists in the
    raw dictionary. If it does, the corresponding value is cast using the
    provided type callable. If it does not, the provided default value is used.

    Args:
        raw: A dictionary with raw input values.
        schema: A dictionary mapping field names to a tuple of
                (type_callable, default_value). The type_callable is a function
                (e.g., int, str) used to convert the raw value. The
                default_value is used when the key is missing from `raw`.

    Returns:
        A new dictionary with fields and values conforming to the schema.

    Raises:
        ValueError: If a value from `raw` cannot be cast using the
                    corresponding type callable from the schema. The error
                    message will include the name of the field that failed.
    """
    coerced_data = {}
    for field_name, (type_callable, default) in schema.items():
        if field_name in raw:
            raw_value = raw[field_name]
            try:
                coerced_value = type_callable(raw_value)
            except (ValueError, TypeError) as e:
                # Catch common casting errors and raise a more specific error
                # as required by the task.
                raise ValueError(f"Failed to cast field '{field_name}'") from e
            coerced_data[field_name] = coerced_value
        else:
            coerced_data[field_name] = default
    return coerced_data
