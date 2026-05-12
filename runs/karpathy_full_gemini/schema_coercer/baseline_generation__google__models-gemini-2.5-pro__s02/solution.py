"""
Provides a function to coerce raw dictionary data into a structured and typed
format according to a given schema.
"""

import typing

# Define a type alias for the schema structure for clarity and reusability.
# The schema maps a field name (str) to a tuple containing:
# 1. A callable that takes one argument and returns a coerced value.
# 2. A default value to be used if the field is missing from the raw data.
SchemaType = typing.Dict[
    str,
    typing.Tuple[typing.Callable[[typing.Any], typing.Any], typing.Any]
]


def coerce_schema(
    raw: typing.Dict[str, typing.Any],
    schema: SchemaType
) -> typing.Dict[str, typing.Any]:
    """
    Coerces a raw dictionary to a typed dictionary based on a schema.

    The schema defines the expected fields, their types, and default values.
    For each field in the schema:
    - If the field exists in the raw dictionary, its value is cast using the
      provided type callable.
    - If the field is missing from the raw dictionary, the default value from
      the schema is used.
    - Any fields in the raw dictionary that are not in the schema are ignored.

    Args:
        raw: The raw input dictionary with string keys.
        schema: A dictionary mapping field names to a tuple of
                (type_callable, default_value). `type_callable` is a function
                used to cast the value (e.g., int, str), and `default_value`
                is used when the key is missing in `raw`.

    Returns:
        A new dictionary with the coerced data, conforming to the schema.

    Raises:
        ValueError: If casting a value from the raw dictionary fails (e.g.,
                    trying to cast a non-numeric string to an integer), a
                    ValueError is raised with a message indicating which field
                    caused the failure.
    """
    coerced_data: typing.Dict[str, typing.Any] = {}

    for field_name, (type_callable, default_value) in schema.items():
        if field_name in raw:
            raw_value = raw[field_name]
            try:
                coerced_value = type_callable(raw_value)
            except (ValueError, TypeError) as e:
                # The original exception is chained for better traceback and
                # debugging, while fulfilling the requirement to raise a
                # ValueError that includes the problematic field name.
                raise ValueError(
                    f"Failed to cast field '{field_name}'"
                ) from e
        else:
            coerced_value = default_value

        coerced_data[field_name] = coerced_value

    return coerced_data
