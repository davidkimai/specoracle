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
        {"input": str, "limit": int, "format": str, "dry_run": bool}

    Raises
    ------
    ValueError
        For missing required flags, unknown flags, missing values, or invalid values.
    """
    # Defaults
    result = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    # Flags that expect a following value argument
    VALUE_FLAGS = {"--input", "--limit", "--format"}
    # Boolean flags (no following value)
    BOOL_FLAGS = {"--dry-run"}
    ALL_KNOWN_FLAGS = VALUE_FLAGS | BOOL_FLAGS

    i = 0
    while i < len(argv):
        token = argv[i]

        if not token.startswith("--"):
            raise ValueError(
                f"Unexpected positional argument or invalid token: {token!r}"
            )

        if token not in ALL_KNOWN_FLAGS:
            raise ValueError(f"Unknown flag: {token!r}")

        if token in BOOL_FLAGS:
            if token == "--dry-run":
                result["dry_run"] = True
            i += 1
            continue

        # token is a value flag — need the next token as its value
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
                limit_int = int(value)
            except ValueError:
                raise ValueError(
                    f"--limit requires a positive integer, got {value!r}."
                )
            if limit_int <= 0:
                raise ValueError(
                    f"--limit must be a positive integer, got {limit_int}."
                )
            result["limit"] = limit_int

        elif token == "--format":
            if value not in ("json", "csv"):
                raise ValueError(
                    f"--format must be 'json' or 'csv', got {value!r}."
                )
            result["format"] = value

        i += 2

    # Validate required flags
    if result["input"] is None:
        raise ValueError("Missing required flag: --input")

    return result
