"""
cli_argument_validation.py

Implements parse_cli_args(argv: list[str]) -> dict for validating and parsing
a specific set of CLI flags without calling sys.exit.
"""


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parse and validate a list of CLI argument strings.

    Supported flags:
        --input PATH      Required. Path string.
        --limit N         Optional. Positive integer. Default: 100.
        --format VALUE    Optional. Must be "json" or "csv". Default: "json".
        --dry-run         Optional boolean flag. Default: False.
        --tag KEY=VALUE   Optional, repeatable. Builds a "tags" dict.
                          Duplicate keys use the last value.

    Returns:
        dict with keys: "input" (str), "limit" (int), "format" (str),
                        "dry_run" (bool), "tags" (dict).

    Raises:
        ValueError: For missing required flags, unknown flags, missing values,
                    or invalid values.
    """
    known_flags = {"--input", "--limit", "--format", "--dry-run", "--tag"}
    value_flags = {"--input", "--limit", "--format", "--tag"}

    result = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
        "tags": {},
    }

    i = 0
    while i < len(argv):
        token = argv[i]

        if not token.startswith("--"):
            raise ValueError(
                f"Unexpected argument: {token!r}. All arguments must start with '--'."
            )

        if token not in known_flags:
            raise ValueError(f"Unknown flag: {token!r}.")

        if token in value_flags:
            # Expect a value in the next position
            if i + 1 >= len(argv):
                raise ValueError(f"Flag {token!r} requires a value but none was provided.")
            next_token = argv[i + 1]
            if next_token.startswith("--"):
                raise ValueError(
                    f"Flag {token!r} requires a value but got another flag {next_token!r}."
                )

            if token == "--input":
                result["input"] = next_token
            elif token == "--limit":
                try:
                    limit_value = int(next_token)
                except ValueError:
                    raise ValueError(
                        f"Flag --limit requires a positive integer, got {next_token!r}."
                    )
                if limit_value <= 0:
                    raise ValueError(
                        f"Flag --limit must be a positive integer, got {limit_value}."
                    )
                result["limit"] = limit_value
            elif token == "--format":
                if next_token not in ("json", "csv"):
                    raise ValueError(
                        f"Flag --format must be 'json' or 'csv', got {next_token!r}."
                    )
                result["format"] = next_token
            elif token == "--tag":
                if "=" not in next_token:
                    raise ValueError(
                        f"Flag --tag requires a value in KEY=VALUE format, got {next_token!r}."
                    )
                tag_key, tag_value = next_token.split("=", 1)
                if not tag_key:
                    raise ValueError(
                        f"Flag --tag has an empty key in {next_token!r}."
                    )
                result["tags"][tag_key] = tag_value

            i += 2  # Advance past the flag and its value
        else:
            # Boolean flag: --dry-run
            if token == "--dry-run":
                result["dry_run"] = True
            i += 1

    # Validate required flags
    if result["input"] is None:
        raise ValueError("Required flag --input is missing.")

    return result
