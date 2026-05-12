"""A module for coercing a raw dictionary to a specified schema."""

import typing


def _validate_spec(field_name: str, spec: typing.Any) -> None:
    """
    Validate that a schema specification for a field is well-formed.

    A valid spec is a tuple of (callable, default_value).

    Raises:
        TypeError: If the spec is not a tuple of length 2, or if the first
                   element is not callable.
    """
    if not isinstance(spec, tuple) or len(spec) != 2:
        raise TypeError(
            f"Schema spec for field '{field_name}' must be a (type_callable, default) tuple."
        )

    type_callable, _ = spec
    if not callable(type_callable):
        raise TypeError(f"Schema type for field '{field_name}' must be a callable.")


def _coerce_value(
    field_name: str, raw_value: typing.Any, type_callable: typing.Callable
) -> typing.Any:
    """
    Apply the type callable to a raw value, handling casting errors.

    Raises:
        ValueError: If the type_callable raises ValueError or TypeError,
                    indicating a failed cast.
    """
    try:
        return type_callable(raw_value)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to cast value for field '{field_name}'.") from e


def coerce_schema(
    raw: typing.Dict[str, typing.Any],
    schema: typing.Dict[str, typing.Tuple[typing.Callable, typing.Any]],
) -> typing.Dict[str, typing.Any]:
    """
    Coerce a raw dictionary to conform to a given schema.

    For each field in the schema, this function checks if the field exists
    in the raw data.
    - If it exists, the corresponding value is cast using the type_callable
      from the schema.
    - If it is missing, the default value from the schema is used.
    - Extra fields in the raw data that are not in the schema are ignored.

    The schema is a dictionary mapping field names to a tuple of
    (type_callable, default_value).

    Args:
        raw: A dictionary of raw data.
        schema: A dictionary defining the desired types and defaults.

    Returns:
        A new dictionary with data coerced according to the schema.

    Raises:
        TypeError: If `raw` or `schema` are not dictionaries, or if the
                   schema itself is malformed.
        ValueError: If a value from the raw data cannot be cast to the
                    type specified in the schema.
    """
    if not isinstance(raw, dict):
        raise TypeError(f"raw data must be a dict, not {type(raw).__name__}.")
    if not isinstance(schema, dict):
        raise TypeError(f"schema must be a dict, not {type(schema).__name__}.")

    coerced_data: typing.Dict[str, typing.Any] = {}

    for field_name, spec in schema.items():
        _validate_spec(field_name, spec)
        type_callable, default = spec

        if field_name in raw:
            raw_value = raw[field_name]
            coerced_value = _coerce_value(field_name, raw_value, type_callable)
            coerced_data[field_name] = coerced_value
        else:
            coerced_data[field_name] = default

    return coerced_data
