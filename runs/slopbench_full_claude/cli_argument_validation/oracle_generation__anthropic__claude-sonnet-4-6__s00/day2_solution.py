"""
cli_argument_validation.py

Parses a list of CLI argument strings into a validated configuration dict.
"""

from __future__ import annotations


_VALID_FORMATS = {"json", "csv"}
_DEFAULT_LIMIT = 100
_DEFAULT_FORMAT = "json"


def _parse_tokens(argv: list[str]) -> tuple[dict[str, str | bool | None], list[str]]:
    """
    Walk argv left-to-right, collecting flag/value pairs.

    Returns a tuple of:
    - raw dict mapping canonical flag names to their string values
      (or True for boolean flags).
    - list of raw --tag values (possibly repeated).

    Raises ValueError on structural problems.
    """
    known_flags = {"--input", "--limit", "--format", "--dry-run", "--tag"}
    value_flags = {"--input", "--limit", "--format", "--tag"}

    raw: dict[str, str | bool] = {}
    tag_values: list[str] = []
    index = 0

    while index < len(argv):
        token = argv[index]

        if not token.startswith("--"):
            raise ValueError(f"Unexpected positional argument: {token!r}")

        if token not in known_flags:
            raise ValueError(f"Unknown flag: {token!r}")

        if token == "--dry-run":
            raw["--dry-run"] = True
            index += 1
            continue

        # token is a value flag; the next token must be its value
        if index + 1 >= len(argv):
            raise ValueError(f"Flag {token!r} requires a value but none was provided")

        next_token = argv[index + 1]
        if next_token.startswith("--"):
            raise ValueError(
                f"Flag {token!r} requires a value but got flag {next_token!r}"
            )

        if token == "--tag":
            tag_values.append(next_token)
            index += 2
            continue

        if token in raw:
            raise ValueError(f"Flag {token!r} specified more than once")

        raw[token] = next_token
        index += 2

    return raw, tag_values


def _coerce_limit(raw_value: str) -> int:
    """Convert a raw string to a positive integer limit."""
    try:
        value = int(raw_value)
    except ValueError:
        raise ValueError(
            f"--limit must be an integer, got {raw_value!r}"
        )
    if value <= 0:
        raise ValueError(
            f"--limit must be a positive integer, got {value}"
        )
    return value


def _coerce_format(raw_value: str) -> str:
    """Validate and return the format string."""
    if raw_value not in _VALID_FORMATS:
        raise ValueError(
            f"--format must be one of {sorted(_VALID_FORMATS)}, got {raw_value!r}"
        )
    return raw_value


def _coerce_tags(tag_values: list[str]) -> dict[str, str]:
    """
    Parse a list of KEY=VALUE strings into a dict.

    Duplicate keys use the last value.  Raises ValueError if any entry
    does not contain '='.
    """
    tags: dict[str, str] = {}
    for entry in tag_values:
        if "=" not in entry:
            raise ValueError(
                f"--tag value must be in KEY=VALUE format, got {entry!r}"
            )
        key, _, value = entry.partition("=")
        if not key:
            raise ValueError(
                f"--tag key must not be empty, got {entry!r}"
            )
        tags[key] = value
    return tags


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parse and validate CLI arguments.

    Parameters
    ----------
    argv:
        List of argument strings (e.g. sys.argv[1:]).

    Returns
    -------
    dict with keys: input (str), limit (int), format (str), dry_run (bool),
    tags (dict[str, str]).

    Raises
    ------
    ValueError
        On missing required flags, unknown flags, missing values, or invalid values.
    """
    raw, tag_values = _parse_tokens(argv)

    if "--input" not in raw:
        raise ValueError("Required flag --input is missing")

    input_path: str = raw["--input"]  # type: ignore[assignment]

    limit_raw = raw.get("--limit")
    limit = _coerce_limit(limit_raw) if limit_raw is not None else _DEFAULT_LIMIT  # type: ignore[arg-type]

    format_raw = raw.get("--format")
    fmt = _coerce_format(format_raw) if format_raw is not None else _DEFAULT_FORMAT  # type: ignore[arg-type]

    dry_run: bool = raw.get("--dry-run", False)  # type: ignore[assignment]

    tags = _coerce_tags(tag_values)

    return {
        "input": input_path,
        "limit": limit,
        "format": fmt,
        "dry_run": dry_run,
        "tags": tags,
    }
