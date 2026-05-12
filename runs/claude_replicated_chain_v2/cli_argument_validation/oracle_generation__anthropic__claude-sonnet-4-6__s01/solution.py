"""
cli_argument_validation.py

Parse a small fixed set of CLI flags from a list of strings.
"""

from __future__ import annotations


_VALID_FORMATS = {"json", "csv"}
_KNOWN_FLAGS = {"--input", "--limit", "--format", "--dry-run"}


def _require_next_value(flag: str, argv: list[str], index: int) -> str:
    """Return the value token that must follow *flag* at *index*."""
    if index >= len(argv):
        raise ValueError(f"Flag '{flag}' requires a value but none was provided.")
    value = argv[index]
    if value.startswith("--"):
        raise ValueError(
            f"Flag '{flag}' requires a value but found another flag: '{value}'."
        )
    return value


def _parse_limit(raw: str) -> int:
    """Convert *raw* to a positive integer or raise ValueError."""
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(
            f"--limit requires a positive integer, got: '{raw}'."
        )
    if value <= 0:
        raise ValueError(
            f"--limit must be a positive integer, got: {value}."
        )
    return value


def _parse_format(raw: str) -> str:
    """Validate that *raw* is an accepted format string."""
    if raw not in _VALID_FORMATS:
        raise ValueError(
            f"--format must be one of {sorted(_VALID_FORMATS)}, got: '{raw}'."
        )
    return raw


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parse *argv* (a list of string tokens, not including the program name)
    and return a validated options dictionary.

    Raises ValueError for any validation failure.
    """
    result: dict = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    index = 0
    while index < len(argv):
        token = argv[index]

        if not token.startswith("--"):
            raise ValueError(f"Unexpected positional argument: '{token}'.")

        if token not in _KNOWN_FLAGS:
            raise ValueError(f"Unknown flag: '{token}'.")

        if token == "--dry-run":
            result["dry_run"] = True
            index += 1
            continue

        # All remaining flags expect a following value token.
        index += 1
        raw_value = _require_next_value(token, argv, index)
        index += 1

        if token == "--input":
            result["input"] = raw_value
        elif token == "--limit":
            result["limit"] = _parse_limit(raw_value)
        elif token == "--format":
            result["format"] = _parse_format(raw_value)

    if result["input"] is None:
        raise ValueError("Required flag '--input' is missing.")

    return result
