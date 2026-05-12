"""
A module for parsing and validating command-line arguments.
"""

def parse_cli_args(argv: list[str]) -> dict:
    """
    Parses and validates a list of command-line arguments.

    Args:
        argv: A list of strings representing the command-line arguments,
              typically from sys.argv[1:].

    Returns:
        A dictionary containing the parsed arguments:
        {
            "input": str,
            "limit": int,
            "format": str,
            "dry_run": bool,
        }

    Raises:
        ValueError: If arguments are invalid. This includes missing required
                    flags, unknown flags, missing values for flags, or
                    invalid values.
    """
    # Default values for optional arguments.
    # `input` is required, so we initialize to None and check for it at the end.
    args = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    # Define the set of all supported flags for validation.
    known_flags_with_values = {"--input", "--limit", "--format"}
    known_boolean_flags = {"--dry-run"}
    all_known_flags = known_flags_with_values.union(known_boolean_flags)

    i = 0
    while i < len(argv):
        arg = argv[i]

        if not arg.startswith('--'):
            raise ValueError(f"Unexpected argument: {arg}")

        if arg not in all_known_flags:
            raise ValueError(f"Unknown flag: {arg}")

        if arg in known_boolean_flags:
            if arg == "--dry-run":
                args["dry_run"] = True
            # No value to consume for boolean flags.
            i += 1
            continue

        # At this point, the flag must be one that requires a value.
        # Check if a value is provided (i.e., it exists and is not another flag).
        if i + 1 >= len(argv) or argv[i + 1].startswith('--'):
            raise ValueError(f"Missing value for flag: {arg}")

        value = argv[i + 1]

        if arg == "--input":
            args["input"] = value
        elif arg == "--limit":
            try:
                limit_val = int(value)
                if limit_val <= 0:
                    # Raise to be caught by the same handler below.
                    raise ValueError()
            except ValueError:
                # Use `from None` to prevent chaining the original exception.
                raise ValueError(
                    f"Invalid value for --limit: '{value}'. Must be a positive integer."
                ) from None
            args["limit"] = limit_val
        elif arg == "--format":
            allowed_formats = {"json", "csv"}
            if value not in allowed_formats:
                raise ValueError(
                    f"Invalid value for --format: '{value}'. Must be 'json' or 'csv'."
                )
            args["format"] = value

        # Move past the flag and its value.
        i += 2

    # Final validation for required arguments.
    if args["input"] is None:
        raise ValueError("Missing required flag: --input")

    return args
