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
        --format VALUE    Optional. "json" or "csv". Default: "json".
        --dry-run         Optional boolean flag. Default: False.

    Returns:
        dict with keys: "input" (str), "limit" (int), "format" (str), "dry_run" (bool)

    Raises:
        ValueError: for missing required flags, unknown flags, missing values,
                    or invalid values.
    """
    known_value_flags = {"--input", "--limit", "--format"}
    known_bool_flags = {"--dry-run"}

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
            raise ValueError(f"Unknown or unexpected argument: {token!r}")

        if token in known_bool_flags:
            if token == "--dry-run":
                result["dry_run"] = True
            i += 1
            continue

        if token in known_value_flags:
            # Expect a following value
            if i + 1 >= len(argv):
                raise ValueError(f"Flag {token!r} requires a value but none was provided.")
            value = argv[i + 1]
            if value.startswith("--"):
                raise ValueError(
                    f"Flag {token!r} requires a value but got another flag {value!r}."
                )

            if token == "--input":
                result["input"] = value

            elif token == "--limit":
                try:
                    limit_val = int(value)
                except ValueError:
                    raise ValueError(
                        f"--limit requires a positive integer, got {value!r}."
                    )
                if limit_val <= 0:
                    raise ValueError(
                        f"--limit must be a positive integer, got {limit_val}."
                    )
                result["limit"] = limit_val

            elif token == "--format":
                if value not in ("json", "csv"):
                    raise ValueError(
                        f"--format must be 'json' or 'csv', got {value!r}."
                    )
                result["format"] = value

            i += 2
            continue

        # Token starts with "--" but is not in known flags
        raise ValueError(f"Unknown flag: {token!r}")

    # Validate required flags
    if result["input"] is None:
        raise ValueError("--input is required but was not provided.")

    return result
