import sys
from typing import Any, Callable, Dict, Tuple

if sys.version_info < (3, 9):
    from typing import Dict as DictType
else:
    DictType = dict


def _coerce_field(
    field_name: str, raw_value: Any, type_callable: Callable[[Any], Any]
) -> Any:
    """
    Applies a type callable to a raw value, wrapping exceptions for context.

    Args:
        field_name: The name of the field being coerced, for error reporting.
        raw_value: The input value to coerce.
        type_callable: The function to apply for coercion (e.g., int, str).

    Returns:
        The coerced value.

    Raises:
        ValueError: If the type_callable raises ValueError or TypeError during
                    casting, indicating a failure to coerce the value.
    """
    try:
        return type_callable(raw_value)
    except (ValueError, TypeError) as e:
        # Re-raise with a more specific message including the field name.
        raise ValueError(f"Failed to cast field '{field_name}'") from e


def coerce_schema(raw: Dict[str, Any], schema: Dict[str, tuple]) -> Dict[str, Any]:
    """
    Coerces a raw dictionary to conform to a given schema.

    For each field in the schema, this function attempts to find a corresponding
    value in the raw dictionary. If found, it casts the value using the
    schema's specified type callable. If not found, it uses the schema's
    default value.

    The schema format is a dictionary where keys are field names and values are
    tuples of (type_callable, default_value). For example:
    {
        'user_id': (int, 0),
        'is_active': (bool, False),
    }

    Args:
        raw: A dictionary of raw input values.
        schema: A dictionary defining the desired fields, types, and defaults.

    Returns:
        A new dictionary with fields from the schema, with values either
        cast from the raw input or set to their default.

    Raises:
        ValueError: If a value from the raw dictionary cannot be cast, or if
                    the schema format for a field is invalid.
        TypeError: If `raw` or `schema` are not dictionaries, or if a schema
                   specifies a non-callable type.
    """
    if not isinstance(raw, dict):
        raise TypeError(f"raw data must be a dict, but got {type(raw).__name__}.")
    if not isinstance(schema, dict):
        raise TypeError(f"schema must be a dict, but got {type(schema).__name__}.")

    coerced_data: DictType[str, Any] = {}

    for field_name, spec in schema.items():
        if not isinstance(spec, tuple) or len(spec) != 2:
            raise ValueError(
                f"Invalid schema format for field '{field_name}': "
                f"expected (type_callable, default), but got {spec!r}."
            )

        type_callable, default_value = spec

        if not callable(type_callable):
            raise TypeError(
                f"Schema for field '{field_name}' requires a callable, "
                f"but got object of type {type(type_callable).__name__}."
            )

        if field_name in raw:
            raw_value = raw[field_name]
            coerced_data[field_name] = _coerce_field(
                field_name, raw_value, type_callable
            )
        else:
            coerced_data[field_name] = default_value

    return coerced_data
