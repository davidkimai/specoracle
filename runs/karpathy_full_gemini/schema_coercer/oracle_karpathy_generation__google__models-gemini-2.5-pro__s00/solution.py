import typing

def coerce_schema(raw: dict, schema: dict) -> dict:
    """
    Coerces a raw dictionary to a typed dictionary based on a schema.

    For each field defined in the schema, this function processes the
    corresponding value from the raw input dictionary. If a field exists in the
    raw dictionary, its value is cast using the provided type callable. If the
    field is missing, a default value from the schema is used. Fields in the
    raw dictionary that are not defined in the schema are ignored.

    Args:
        raw: A dictionary containing raw input data. Keys are field names, and
             values are the data to be processed.
        schema: A dictionary that defines the target structure and types. Each
                key is a field name, and the corresponding value is a tuple of
                (type_callable, default_value). The `type_callable` is a
                function (e.g., int, str) that takes a single argument and
                returns the coerced value. The `default_value` is used when
                the field is absent from the `raw` dictionary.

    Returns:
        A new dictionary with fields and values conforming to the schema.

    Raises:
        ValueError: If a type casting operation fails for a specific field.
                    The error message will include the name of the field that
                    caused the failure.
    """
    coerced_data = {}
    for field_name, (type_callable, default_value) in schema.items():
        if field_name in raw:
            raw_value = raw[field_name]
            try:
                coerced_value = type_callable(raw_value)
            except (ValueError, TypeError) as e:
                # Catch common casting exceptions and re-raise as a ValueError
                # with a more informative message, as per requirements.
                raise ValueError(
                    f"Failed to cast field '{field_name}' with value "
                    f"'{raw_value}' to type {type_callable.__name__}"
                ) from e
            coerced_data[field_name] = coerced_value
        else:
            coerced_data[field_name] = default_value
    return coerced_data
