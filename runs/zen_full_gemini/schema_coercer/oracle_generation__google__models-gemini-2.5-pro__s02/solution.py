"""
A module for coercing raw dictionary data to a specified schema.
"""

from typing import Any, Callable, Dict, Tuple

# A type alias for the schema structure for better readability and maintainability.
# Schema is a dictionary where keys are field names (str), and values are tuples
# containing a callable for type casting and a default value.
Schema = Dict[str, Tuple[Callable[[Any], Any], Any]]


def _validate_schema_entry(field_name: str, schema_entry: Any) -> None:
    """Checks if a schema entry is a valid (callable, default) tuple."""
    if not isinstance(schema_entry, tuple) or len(schema_entry) != 2:
        raise TypeError(
            f"Schema entry for '{field_name}' must be a (type_callable, default) tuple."
        )

    type_callable, _ = schema_entry
    if not callable(type_callable):
        raise TypeError(
            f"Type caster for field '{field_name}' must be a callable."
        )


def _apply_type_callable(
    field_name: str, type_callable: Callable[[Any], Any], raw_value: Any
) -> Any:
    """Applies the type callable to a raw value, handling potential errors."""
    try:
        return type_callable(raw_value)
    except (ValueError, TypeError) as e:
        # Re-raise as ValueError to provide a consistent error type for coercion failures.
        raise ValueError(
            f"Failed to cast field '{field_name}' with value {raw_value!r}."
        ) from e


def coerce_schema(raw: Dict[str, Any], schema: Schema) -> Dict[str, Any]:
    """
    Coerces a raw dictionary to conform to a given schema.

    For each field defined in the schema, this function applies a type casting
    callable to the corresponding value in the raw dictionary. If a field is
    missing from the raw dictionary, a specified default value is used instead.

    The function processes only the fields present in the schema. Any extra
    fields in the raw dictionary are ignored.

    Args:
        raw: The input dictionary containing raw data.
        schema: A dictionary that defines the schema. Each key is a field name,
                and its value is a tuple of (type_callable, default_value).
                - `type_callable`: A function to cast the raw value (e.g., int, str).
                - `default_value`: The value to use if the field is not in `raw`.

    Returns:
        A new dictionary with data coerced according to the schema.

    Raises:
        ValueError: If a type casting operation fails for any field. The error
                    message will include the field name and the problematic value.
        TypeError: If `raw` or `schema` are not dictionaries, or if a schema
                   entry is not a (callable, default) tuple.
    """
    if not isinstance(raw, dict):
        raise TypeError("Argument 'raw' must be a dictionary.")
    if not isinstance(schema, dict):
        raise TypeError("Argument 'schema' must be a dictionary.")

    coerced_data = {}

    for field_name, schema_entry in schema.items():
        _validate_schema_entry(field_name, schema_entry)
        type_callable, default_value = schema_entry

        if field_name in raw:
            raw_value = raw[field_name]
            coerced_value = _apply_type_callable(
                field_name, type_callable, raw_value
            )
            coerced_data[field_name] = coerced_value
        else:
            coerced_data[field_name] = default_value

    return coerced_data
