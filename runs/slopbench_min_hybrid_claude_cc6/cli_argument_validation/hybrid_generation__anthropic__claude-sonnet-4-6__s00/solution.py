"""CLI argument validation module."""


def _next_value(argv: list[str], index: int, flag: str) -> str:
    """Return the value token following a flag, or raise ValueError."""
    if index + 1 >= len(argv):
        raise ValueError(f"Flag {flag!r} requires a value but none was provided")
    next_token = argv[index + 1]
    if next_token.startswith("--"):
        raise ValueError(f"Flag {flag!r} requires a value but got flag {next_token!r}")
    return next_token


def _check_known(token: str, known_flags: set) -> None:
    """Raise ValueError if token is not a known flag."""
    if token not in known_flags:
        raise ValueError(f"Unknown flag: {token!r}")


def _check_flag_shape(token: str) -> None:
    """Raise ValueError if token does not look like a flag."""
    if not token.startswith("--"):
        raise ValueError(f"Unexpected argument: {token!r}")


def _collect_raw(argv: list[str]) -> dict:
    """Walk argv and collect raw flag -> value mappings."""
    known_flags = {"--input", "--limit", "--format", "--dry-run"}
    value_flags = {"--input", "--limit", "--format"}
    raw = {}
    index = 0
    while index < len(argv):
        token = argv[index]
        _check_flag_shape(token)
        _check_known(token, known_flags)
        if token in value_flags:
            raw[token] = _next_value(argv, index, token)
            index += 2
        else:
            raw[token] = True
            index += 1
    return raw


def _require_input(raw: dict) -> str:
    """Extract and return the required --input value."""
    if "--input" not in raw:
        raise ValueError("Required flag --input is missing")
    return raw["--input"]


def _parse_limit(value) -> int:
    """Parse and validate the --limit value, defaulting to 100."""
    if value is None:
        return 100
    try:
        limit = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"--limit must be an integer, got {value!r}")
    if limit <= 0:
        raise ValueError(f"--limit must be a positive integer, got {limit}")
    return limit


def _parse_format(value) -> str:
    """Parse and validate the --format value, defaulting to 'json'."""
    if value is None:
        return "json"
    allowed = {"json", "csv"}
    if value not in allowed:
        raise ValueError(f"--format must be one of {sorted(allowed)}, got {value!r}")
    return value


def _build_result(raw: dict) -> dict:
    """Validate parsed raw flags and build the result dictionary."""
    return {
        "input": _require_input(raw),
        "limit": _parse_limit(raw.get("--limit")),
        "format": _parse_format(raw.get("--format")),
        "dry_run": raw.get("--dry-run", False),
    }


def parse_cli_args(argv: list[str]) -> dict:
    """Parse and validate CLI arguments from a list of strings.

    Args:
        argv: List of argument strings (excluding the program name).

    Returns:
        Dictionary with keys: input, limit, format, dry_run.

    Raises:
        ValueError: For missing required flags, unknown flags, missing values,
                    or invalid values.
    """
    raw = _collect_raw(argv)
    return _build_result(raw)
