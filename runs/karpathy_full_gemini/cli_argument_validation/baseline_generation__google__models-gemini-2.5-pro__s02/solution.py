import typing


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parses and validates command-line arguments from a list of strings.

    This function implements a command-line parser for a specific set of flags.
    It is designed to be self-contained and raise ValueErrors on any parsing
    or validation failures, rather than exiting the program.

    Supported flags:
    - --input PATH: Required. Specifies the input path.
    - --limit N: Optional. A positive integer, defaults to 100.
    - --format VALUE: Optional. Must be "json" or "csv", defaults to "json".
    - --dry-run: Optional. A boolean flag that takes no value.

    Args:
        argv: A list of string arguments, conventionally sys.argv[1:].

    Returns:
        A dictionary containing the parsed and validated arguments with the
        following structure:
        {
            "input": str,
            "limit": int,
            "format": str,
            "dry_run": bool
        }

    Raises:
        ValueError: If arguments are invalid. This includes missing required
                    flags, unknown flags, flags with missing values, or flags
                    with values that fail validation (e.g., wrong type,
                    out of range, not in allowed set).
    """
    parsed_args: dict[str, typing.Any] = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    flags_with_values = {"--input", "--limit", "--format"}
    boolean_flags = {"--dry-run"}
    known_flags = flags_with_values.union(boolean_flags)

    i = 0
    while i < len(argv):
        arg = argv[i]

        if not arg.startswith('--'):
            raise ValueError(f"Unexpected positional argument: '{arg}'")

        if arg not in known_flags:
            raise ValueError(f"Unknown flag: '{arg}'")

        if arg in boolean_flags:
            if arg == "--dry-run":
                parsed_args["dry_run"] = True
            i += 1
            continue

        # At this point, the flag must be one that takes a value.
        if i + 1 >= len(argv) or argv[i + 1].startswith('--'):
            raise ValueError(f"Missing value for flag: '{arg}'")

        value = argv[i + 1]

        if arg == "--input":
            parsed_args["input"] = value
        elif arg == "--limit":
            try:
                limit_val = int(value)
                if limit_val <= 0:
                    # Create a new ValueError to provide a clear message
                    raise ValueError("must be a positive integer")
                parsed_args["limit"] = limit_val
            except ValueError as e:
                # Chain the exception for better debugging
                raise ValueError(
                    f"Invalid value for --limit: '{value}'. {e}"
                ) from e
        elif arg == "--format":
            if value not in ("json", "csv"):
                raise ValueError(
                    f"Invalid value for --format: '{value}'. Must be 'json' or 'csv'."
                )
            parsed_args["format"] = value

        # Move past the flag and its value
        i += 2

    # Final validation for required arguments
    if parsed_args["input"] is None:
        raise ValueError("Missing required flag: --input")

    return parsed_args
