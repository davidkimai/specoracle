"""
cli_argument_validation.py

Parses a list of CLI argument strings and returns a validated dictionary.
"""


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parse and validate CLI arguments.

    Supported flags:
        --input PATH      Required. Path string.
        --limit N         Optional. Positive integer. Default: 100.
        --format VALUE    Optional. One of "json" or "csv". Default: "json".
        --dry-run         Optional boolean flag. Default: False.

    Returns:
        dict with keys: "input" (str), "limit" (int), "format" (str), "dry_run" (bool)

    Raises:
        ValueError: on missing required flags, unknown flags, missing values,
                    or invalid values.
    """
    known_flags = {"--input", "--limit", "--format", "--dry-run"}
    value_flags = {"--input", "--limit", "--format"}

    result = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    i = 0
    while i < len(argv):
        token = argv[i]

        if not token.startswith("--"):
            raise ValueError(
                f"Unexpected argument '{token}'. All arguments must be flags starting with '--'."
            )

        if token not in known_flags:
            raise ValueError(f"Unknown flag: '{token}'.")

        if token in value_flags:
            # Expect a value to follow
            if i + 1 >= len(argv):
                raise ValueError(f"Flag '{token}' requires a value but none was provided.")
            next_token = argv[i + 1]
            if next_token.startswith("--"):
                raise ValueError(
                    f"Flag '{token}' requires a value but got another flag '{next_token}'."
                )
            value = next_token
            i += 2

            if token == "--input":
                result["input"] = value

            elif token == "--limit":
                try:
                    limit_val = int(value)
                except ValueError:
                    raise ValueError(
                        f"--limit requires a positive integer, got '{value}'."
                    )
                if limit_val <= 0:
                    raise ValueError(
                        f"--limit must be a positive integer, got {limit_val}."
                    )
                result["limit"] = limit_val

            elif token == "--format":
                if value not in ("json", "csv"):
                    raise ValueError(
                        f"--format must be 'json' or 'csv', got '{value}'."
                    )
                result["format"] = value

        elif token == "--dry-run":
            result["dry_run"] = True
            i += 1

    if result["input"] is None:
        raise ValueError("Required flag '--input' is missing.")

    return result
