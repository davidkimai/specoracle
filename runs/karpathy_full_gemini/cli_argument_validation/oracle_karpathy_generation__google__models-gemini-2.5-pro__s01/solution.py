#
# A solution to the cli_argument_validation task.
#
# This module provides a function to parse and validate command-line arguments
# according to a predefined set of rules.
#

from typing import Any

def parse_cli_args(argv: list[str]) -> dict:
    """
    Parses and validates command-line arguments from a list of strings.

    Args:
        argv: A list of strings representing the command-line arguments,
              excluding the script name (e.g., sys.argv[1:]).

    Returns:
        A dictionary containing the parsed arguments:
        {
            "input": str,      # Path to the input file.
            "limit": int,      # A positive integer limit.
            "format": str,     # "json" or "csv".
            "dry_run": bool    # True if the --dry-run flag is present.
        }

    Raises:
        ValueError: If arguments are invalid, such as a missing required flag,
                    an unknown flag, a flag missing its value, or a flag
                    with an invalid value.
    """
    args: dict[str, Any] = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    flags_with_values = {"--input", "--limit", "--format"}
    boolean_flags = {"--dry-run"}

    i = 0
    while i < len(argv):
        arg = argv[i]

        if arg in flags_with_values:
            if i + 1 >= len(argv) or argv[i + 1].startswith('--'):
                raise ValueError(f"Flag '{arg}' requires a value.")

            value = argv[i + 1]
            i += 2  # Consume flag and value

            if arg == "--input":
                args["input"] = value
            elif arg == "--limit":
                try:
                    limit_val = int(value)
                except ValueError:
                    raise ValueError(
                        f"Value for --limit must be an integer: '{value}'"
                    ) from None

                if limit_val <= 0:
                    raise ValueError(
                        f"Value for --limit must be a positive integer: {limit_val}"
                    )
                args["limit"] = limit_val
            elif arg == "--format":
                if value not in ["json", "csv"]:
                    raise ValueError(
                        f"Value for --format must be 'json' or 'csv': '{value}'"
                    )
                args["format"] = value

        elif arg in boolean_flags:
            if arg == "--dry-run":
                args["dry_run"] = True
            i += 1  # Consume flag

        else:
            raise ValueError(f"Unknown flag: {arg}")

    if args["input"] is None:
        raise ValueError("Missing required flag: --input")

    return args
