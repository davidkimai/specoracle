"""
cli_argument_validation.py

Implements parse_cli_args(argv: list[str]) -> dict for validating and parsing
command-line arguments without using sys.exit.
"""


def parse_cli_args(argv: list) -> dict:
    """
    Parse and validate CLI arguments.

    Supported flags:
        --input PATH       Required. Path string.
        --limit N          Optional. Positive integer. Default: 100.
        --format VALUE     Optional. "json" or "csv". Default: "json".
        --dry-run          Optional boolean flag. Default: False.
        --tag KEY=VALUE    Optional, repeatable. Duplicate keys use last value.

    Returns:
        dict with keys: "input", "limit", "format", "dry_run", "tags"

    Raises:
        ValueError: For missing required flags, unknown flags, missing values,
                    or invalid values.
    """
    known_flags = {"--input", "--limit", "--format", "--dry-run", "--tag"}

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
                f"Unexpected positional argument or unknown token: {token!r}"
            )

        if token not in known_flags:
            raise ValueError(f"Unknown flag: {token!r}")

        if token == "--dry-run":
            result["dry_run"] = True
            i += 1
            continue

        # Flags that require a value
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

        elif token == "--tag":
            if "=" not in value:
                raise ValueError(
                    f"--tag requires a value in KEY=VALUE format, got {value!r}."
                )
            tag_key, tag_val = value.split("=", 1)
            if not tag_key:
                raise ValueError(
                    f"--tag KEY must not be empty, got {value!r}."
                )
            result["tags"][tag_key] = tag_val

        i += 2

    if result["input"] is None:
        raise ValueError("Missing required flag: --input")

    return result
