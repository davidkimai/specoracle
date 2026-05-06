"""
cli_argument_validation.py

Parses a list of CLI argument strings and returns a validated dictionary.
"""


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parse and validate CLI arguments.

    Parameters
    ----------
    argv : list[str]
        List of argument strings (e.g. ["--input", "foo.txt", "--limit", "50"]).

    Returns
    -------
    dict
        {"input": str, "limit": int, "format": str, "dry_run": bool, "tags": dict}

    Raises
    ------
    ValueError
        For missing required flags, unknown flags, missing values, or invalid values.
    """
    # Define recognised flags and whether they take a value argument
    VALUE_FLAGS = {"--input", "--limit", "--format", "--tag"}
    BOOL_FLAGS = {"--dry-run"}
    ALL_FLAGS = VALUE_FLAGS | BOOL_FLAGS

    # Parsed raw storage
    raw: dict = {}
    tags: dict = {}

    i = 0
    while i < len(argv):
        token = argv[i]

        if not token.startswith("--"):
            raise ValueError(
                f"Unexpected positional argument or invalid token: {token!r}. "
                "All arguments must be flags starting with '--'."
            )

        if token not in ALL_FLAGS:
            raise ValueError(f"Unknown flag: {token!r}.")

        if token in BOOL_FLAGS:
            raw[token] = True
            i += 1
        else:  # VALUE_FLAGS
            if i + 1 >= len(argv):
                raise ValueError(
                    f"Flag {token!r} requires a value but none was provided."
                )
            next_token = argv[i + 1]
            if next_token.startswith("--") and next_token in ALL_FLAGS:
                raise ValueError(
                    f"Flag {token!r} requires a value but got another flag "
                    f"{next_token!r} instead."
                )
            if token == "--tag":
                # Parse KEY=VALUE; duplicate keys use the last value
                if "=" not in next_token:
                    raise ValueError(
                        f"Invalid value for --tag: {next_token!r}. "
                        "Must be in KEY=VALUE format."
                    )
                tag_key, tag_val = next_token.split("=", 1)
                if not tag_key:
                    raise ValueError(
                        f"Invalid value for --tag: {next_token!r}. "
                        "Tag key must not be empty."
                    )
                tags[tag_key] = tag_val
            else:
                raw[token] = next_token
            i += 2

    # --- Validate and extract each field ---

    # --input (required)
    if "--input" not in raw:
        raise ValueError("Missing required flag: --input.")
    input_value: str = raw["--input"]

    # --limit (optional, default 100, must be positive integer)
    if "--limit" in raw:
        limit_str = raw["--limit"]
        try:
            limit_value = int(limit_str)
        except ValueError:
            raise ValueError(
                f"Invalid value for --limit: {limit_str!r}. Must be a positive integer."
            )
        if limit_value <= 0:
            raise ValueError(
                f"Invalid value for --limit: {limit_str!r}. Must be a positive integer."
            )
    else:
        limit_value = 100

    # --format (optional, default "json", must be "json" or "csv")
    VALID_FORMATS = {"json", "csv"}
    if "--format" in raw:
        format_value = raw["--format"]
        if format_value not in VALID_FORMATS:
            raise ValueError(
                f"Invalid value for --format: {format_value!r}. "
                f"Must be one of {sorted(VALID_FORMATS)}."
            )
    else:
        format_value = "json"

    # --dry-run (optional boolean flag)
    dry_run_value: bool = raw.get("--dry-run", False)

    return {
        "input": input_value,
        "limit": limit_value,
        "format": format_value,
        "dry_run": dry_run_value,
        "tags": tags,
    }
