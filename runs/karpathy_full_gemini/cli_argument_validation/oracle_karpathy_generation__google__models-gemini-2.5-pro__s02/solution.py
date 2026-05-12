"""A module for parsing and validating command-line arguments."""


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parses and validates command-line arguments.

    Supported flags:
    - --input PATH (required)
    - --limit N (optional, default: 100, must be a positive integer)
    - --format VALUE (optional, default: "json", must be "json" or "csv")
    - --dry-run (optional, boolean flag)

    Args:
        argv: A list of strings representing the command-line arguments,
              excluding the script name.

    Returns:
        A dictionary containing the parsed arguments:
        {
            "input": str,
            "limit": int,
            "format": str,
            "dry_run": bool
        }

    Raises:
        ValueError: If arguments are missing, unknown, or have invalid values.
    """
    args = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    i = 0
    while i < len(argv):
        arg = argv[i]

        if arg == "--input":
            if i + 1 >= len(argv) or argv[i + 1].startswith("-"):
                raise ValueError("Missing value for flag: --input")
            args["input"] = argv[i + 1]
            i += 2
        elif arg == "--limit":
            if i + 1 >= len(argv) or argv[i + 1].startswith("-"):
                raise ValueError("Missing value for flag: --limit")
            value_str = argv[i + 1]
            try:
                limit_val = int(value_str)
                if limit_val <= 0:
                    # Raise to be caught by the same handler below.
                    raise ValueError
                args["limit"] = limit_val
            except ValueError:
                raise ValueError(
                    f"Invalid value for --limit: '{value_str}'. "
                    "Must be a positive integer."
                ) from None
            i += 2
        elif arg == "--format":
            if i + 1 >= len(argv) or argv[i + 1].startswith("-"):
                raise ValueError("Missing value for flag: --format")
            value = argv[i + 1]
            if value not in ["json", "csv"]:
                raise ValueError(
                    f"Invalid value for --format: '{value}'. "
                    "Must be 'json' or 'csv'."
                )
            args["format"] = value
            i += 2
        elif arg == "--dry-run":
            args["dry_run"] = True
            i += 1
        else:
            if arg.startswith("-"):
                raise ValueError(f"Unknown flag: {arg}")
            else:
                raise ValueError(f"Unexpected positional argument: {arg}")

    if args["input"] is None:
        raise ValueError("Missing required flag: --input")

    return args
