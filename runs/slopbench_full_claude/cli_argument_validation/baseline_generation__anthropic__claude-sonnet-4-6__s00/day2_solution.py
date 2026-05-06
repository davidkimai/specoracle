"""
cli_argument_validation.py

Parses a list of CLI argument strings and returns a validated configuration dict.
"""


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parse and validate CLI arguments.

    Parameters
    ----------
    argv : list[str]
        List of argument strings (e.g. ["--input", "file.txt", "--limit", "50"]).

    Returns
    -------
    dict
        {"input": str, "limit": int, "format": str, "dry_run": bool, "tags": dict}

    Raises
    ------
    ValueError
        For missing required flags, unknown flags, missing values, or invalid values.
    """
    # Known flags and whether they expect a following value
    FLAGS_WITH_VALUE = {"--input", "--limit", "--format", "--tag"}
    FLAGS_BOOLEAN = {"--dry-run"}
    ALL_FLAGS = FLAGS_WITH_VALUE | FLAGS_BOOLEAN

    # Raw parsed values
    raw: dict = {}
    tags: dict = {}

    i = 0
    while i < len(argv):
        token = argv[i]

        if not token.startswith("--"):
            raise ValueError(f"Unexpected argument: {token!r}. All arguments must start with '--'.")

        if token not in ALL_FLAGS:
            raise ValueError(f"Unknown flag: {token!r}.")

        if token in FLAGS_BOOLEAN:
            raw[token] = True
            i += 1
        else:
            # Expect a value after the flag
            if i + 1 >= len(argv):
                raise ValueError(f"Flag {token!r} requires a value but none was provided.")
            next_token = argv[i + 1]
            if next_token.startswith("--"):
                raise ValueError(
                    f"Flag {token!r} requires a value but got another flag {next_token!r}."
                )
            if token == "--tag":
                # Parse KEY=VALUE
                if "=" not in next_token:
                    raise ValueError(
                        f"Invalid value for --tag: {next_token!r}. Must be in KEY=VALUE format."
                    )
                key, value = next_token.split("=", 1)
                if not key:
                    raise ValueError(
                        f"Invalid value for --tag: {next_token!r}. Key must not be empty."
                    )
                tags[key] = value
            else:
                raw[token] = next_token
            i += 2

    # --- Validate and build result ---

    # --input (required)
    if "--input" not in raw:
        raise ValueError("Missing required flag: --input.")
    input_value: str = raw["--input"]

    # --limit (optional, default 100, must be positive int)
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
                f"Invalid value for --limit: {limit_value}. Must be a positive integer."
            )
    else:
        limit_value = 100

    # --format (optional, default "json", must be "json" or "csv")
    VALID_FORMATS = {"json", "csv"}
    if "--format" in raw:
        format_value = raw["--format"]
        if format_value not in VALID_FORMATS:
            raise ValueError(
                f"Invalid value for --format: {format_value!r}. Must be one of {sorted(VALID_FORMATS)}."
            )
    else:
        format_value = "json"

    # --dry-run (optional boolean, default False)
    dry_run_value: bool = raw.get("--dry-run", False)

    return {
        "input": input_value,
        "limit": limit_value,
        "format": format_value,
        "dry_run": dry_run_value,
        "tags": tags,
    }
