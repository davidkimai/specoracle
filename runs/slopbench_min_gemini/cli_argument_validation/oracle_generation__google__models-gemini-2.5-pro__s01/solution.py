"""
A module for parsing command-line arguments.

This module provides a function to parse a list of string arguments into a
configuration dictionary, handling validation and error conditions as specified.
"""

from typing import Any


# Defines the command-line interface specification through constants.
# This centralization makes the configuration explicit and easy to audit.

_SUPPORTED_FORMATS: set[str] = {"json", "csv"}

_FLAGS_WITH_VALUE: set[str] = {"--input", "--limit", "--format"}
_BOOLEAN_FLAGS: set[str] = {"--dry-run"}
_KNOWN_FLAGS: set[str] = _FLAGS_WITH_VALUE.union(_BOOLEAN_FLAGS)

_DEFAULT_CONFIG: dict[str, Any] = {
    "input": None,
    "limit": 100,
    "format": "json",
    "dry_run": False,
}


def _parse_limit(value_str: str) -> int:
    """
    Parses and validates the string value for the --limit flag.

    Args:
        value_str: The string value provided for the limit.

    Returns:
        A positive integer representing the limit.

    Raises:
        ValueError: If the value is not a valid positive integer.
    """
    try:
        limit = int(value_str)
    except ValueError:
        raise ValueError(
            f"Invalid value for --limit: '{value_str}' is not an integer."
        ) from None

    if limit <= 0:
        raise ValueError(
            f"Invalid value for --limit: {limit} must be a positive integer."
        )

    return limit


def _parse_format(value_str: str) -> str:
    """
    Parses and validates the string value for the --format flag.

    Args:
        value_str: The string value provided for the format.

    Returns:
        The validated format string, either "json" or "csv".

    Raises:
        ValueError: If the value is not one of the supported formats.
    """
    if value_str not in _SUPPORTED_FORMATS:
        supported_str = ", ".join(f"'{f}'" for f in sorted(_SUPPORTED_FORMATS))
        raise ValueError(
            f"Invalid value for --format: '{value_str}'. Must be one of {supported_str}."
        )
    return value_str


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parses a list of command-line arguments into a configuration dictionary.

    This function implements a simple, strict parser for a predefined set of
    flags. It validates argument types and values, raising errors for any
    deviation from the expected format.

    Args:
        argv: A list of string arguments, typically from sys.argv[1:].

    Returns:
        A dictionary containing the parsed configuration with the structure:
        {
            "input": str,      # Path to the input file.
            "limit": int,      # A positive integer limit.
            "format": str,     # "json" or "csv".
            "dry_run": bool    # True if --dry-run was present.
        }

    Raises:
        ValueError: For any of the following conditions:
            - An unknown flag is provided.
            - A required flag (--input) is missing.
            - A flag that requires a value is missing its value.
            - A flag receives a value of an incorrect type or format.
            - A positional argument is provided.
    """
    config = _DEFAULT_CONFIG.copy()

    i = 0
    while i < len(argv):
        arg = argv[i]

        if not arg.startswith('--'):
            raise ValueError(f"Unexpected positional argument: '{arg}'")

        if arg not in _KNOWN_FLAGS:
            raise ValueError(f"Unknown flag: '{arg}'")

        if arg in _BOOLEAN_FLAGS:
            if arg == "--dry-run":
                config["dry_run"] = True
            i += 1
            continue

        # Argument requires a value.
        if i + 1 >= len(argv) or argv[i + 1].startswith('--'):
            raise ValueError(f"Missing value for flag: '{arg}'")

        value = argv[i + 1]

        if arg == "--input":
            config["input"] = value
        elif arg == "--limit":
            config["limit"] = _parse_limit(value)
        elif arg == "--format":
            config["format"] = _parse_format(value)

        i += 2

    if config["input"] is None:
        raise ValueError("Missing required flag: --input")

    return config
