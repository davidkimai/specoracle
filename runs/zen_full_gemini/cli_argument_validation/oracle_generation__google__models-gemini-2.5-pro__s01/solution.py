import typing

_ALLOWED_FORMATS = {"json", "csv"}
_DEFAULT_LIMIT = 100
_DEFAULT_FORMAT = "json"


def _validate_limit(limit_str: str) -> int:
    """
    Converts a string to a positive integer limit.

    Raises:
        ValueError: If the string is not a positive integer.
    """
    try:
        limit = int(limit_str)
        if limit > 0:
            return limit
    except ValueError:
        # This handles cases where limit_str is not a valid integer literal.
        # The logic falls through to the final raise statement.
        pass

    raise ValueError(
        f"Invalid value for --limit: '{limit_str}'. Must be a positive integer."
    )


def _validate_format(format_str: str) -> str:
    """
    Validates that the format string is one of the allowed values.

    Raises:
        ValueError: If the format is not 'json' or 'csv'.
    """
    if format_str in _ALLOWED_FORMATS:
        return format_str
    raise ValueError(
        f"Invalid value for --format: '{format_str}'. Must be 'json' or 'csv'."
    )


def _parse_raw_args(argv: list[str]) -> dict[str, typing.Union[str, bool]]:
    """
    Parses argv into a raw dictionary of flags and their string or boolean values.

    This helper performs structural checks (e.g., unknown flags, missing values)
    but does not perform type conversion or semantic validation.
    """
    value_flags = {"--input", "--limit", "--format"}
    boolean_flags = {"--dry-run"}
    known_flags = value_flags.union(boolean_flags)

    raw_args: dict[str, typing.Union[str, bool]] = {}
    args_iter = iter(argv)

    for arg in args_iter:
        if arg not in known_flags:
            raise ValueError(f"Unknown flag: '{arg}'")

        if arg in value_flags:
            try:
                value = next(args_iter)
                if value.startswith("-"):
                    raise ValueError(
                        f"Flag '{arg}' requires a value, but found another flag '{value}'."
                    )
                raw_args[arg] = value
            except StopIteration:
                raise ValueError(f"Flag '{arg}' requires a value.") from None

        elif arg in boolean_flags:
            raw_args[arg] = True

    return raw_args


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parses and validates command-line arguments based on predefined rules.

    Args:
        argv: A list of strings representing the command-line arguments,
              typically sys.argv[1:].

    Returns:
        A dictionary containing the parsed and validated arguments:
        {"input": str, "limit": int, "format": str, "dry_run": bool}.

    Raises:
        ValueError: If arguments are missing, unknown, or have invalid values.
        TypeError: If argv is not a list of strings.
    """
    if not isinstance(argv, list) or not all(isinstance(s, str) for s in argv):
        raise TypeError("argv must be a list of strings.")

    raw_args = _parse_raw_args(argv)

    if "--input" not in raw_args:
        raise ValueError("Missing required flag: --input")

    # The type of raw_args["--input"] is guaranteed to be str by _parse_raw_args.
    result: dict[str, typing.Union[str, int, bool]] = {
        "input": str(raw_args["--input"]),
        "limit": _DEFAULT_LIMIT,
        "format": _DEFAULT_FORMAT,
        "dry_run": "--dry-run" in raw_args,
    }

    if "--limit" in raw_args:
        limit_str = typing.cast(str, raw_args["--limit"])
        result["limit"] = _validate_limit(limit_str)

    if "--format" in raw_args:
        format_str = typing.cast(str, raw_args["--format"])
        result["format"] = _validate_format(format_str)

    return result
