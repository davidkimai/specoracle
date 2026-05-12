"""
cli_argument_validation.py

Parses a list of CLI argument strings and returns a validated options dict.
"""

from __future__ import annotations

VALID_FORMATS = ("json", "csv")
DEFAULT_LIMIT = 100
DEFAULT_FORMAT = "json"

# Flags that consume the next token as their value.
VALUE_FLAGS = {"--input", "--limit", "--format"}
# Flags that are boolean switches.
BOOL_FLAGS = {"--dry-run"}
ALL_FLAGS = VALUE_FLAGS | BOOL_FLAGS


def _parse_tokens(argv: list[str]) -> dict[str, str | bool]:
    """
    Walk argv left-to-right, collecting raw flag values.

    Returns a dict mapping flag name -> raw string value (or True for bool flags).
    Raises ValueError for unknown flags, repeated flags, or missing values.
    """
    raw: dict[str, str | bool] = {}
    i = 0
    while i < len(argv):
        token = argv[i]
        if not token.startswith("--"):
            raise ValueError(f"Unexpected positional argument: {token!r}")
        if token not in ALL_FLAGS:
            raise ValueError(f"Unknown flag: {token!r}")
        if token in raw:
            raise ValueError(f"Duplicate flag: {token!r}")
        if token in BOOL_FLAGS:
            raw[token] = True
            i += 1
            continue
        # token is a value flag; next token must be the value
        if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
            raise ValueError(f"Flag {token!r} requires a value but none was provided")
        raw[token] = argv[i + 1]
        i += 2
    return raw


def _require(raw: dict, flag: str) -> str:
    if flag not in raw:
        raise ValueError(f"Required flag {flag!r} is missing")
    return raw[flag]  # type: ignore[return-value]


def _parse_limit(value: str) -> int:
    try:
        n = int(value)
    except ValueError:
        raise ValueError(f"--limit must be an integer, got {value!r}")
    if n <= 0:
        raise ValueError(f"--limit must be a positive integer, got {n}")
    return n


def _parse_format(value: str) -> str:
    if value not in VALID_FORMATS:
        raise ValueError(
            f"--format must be one of {VALID_FORMATS}, got {value!r}"
        )
    return value


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parse a list of CLI argument strings into a validated options dict.

    Parameters
    ----------
    argv:
        Raw argument tokens, e.g. ["--input", "file.txt", "--dry-run"].

    Returns
    -------
    dict with keys: input (str), limit (int), format (str), dry_run (bool).

    Raises
    ------
    ValueError
        For missing required flags, unknown flags, missing values, or invalid values.
    """
    raw = _parse_tokens(argv)

    input_path = _require(raw, "--input")

    limit_raw = raw.get("--limit")
    limit = _parse_limit(limit_raw) if limit_raw is not None else DEFAULT_LIMIT

    format_raw = raw.get("--format")
    fmt = _parse_format(format_raw) if format_raw is not None else DEFAULT_FORMAT

    dry_run = bool(raw.get("--dry-run", False))

    return {
        "input": input_path,
        "limit": limit,
        "format": fmt,
        "dry_run": dry_run,
    }
