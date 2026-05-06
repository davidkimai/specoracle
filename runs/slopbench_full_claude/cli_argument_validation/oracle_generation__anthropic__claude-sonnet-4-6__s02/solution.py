"""cli_argument_validation.py

Parse and validate a fixed set of CLI flags from an argv-style list.
"""

from __future__ import annotations

_VALID_FORMATS = {"json", "csv"}
_DEFAULT_LIMIT = 100
_DEFAULT_FORMAT = "json"


def _consume_value(flag: str, index: int, argv: list[str]) -> str:
    """Return the value token that follows *flag* at *index* in *argv*."""
    next_index = index + 1
    if next_index >= len(argv):
        raise ValueError(f"{flag} requires a value but none was provided")
    value = argv[next_index]
    if value.startswith("--"):
        raise ValueError(f"{flag} requires a value but got flag '{value}' instead")
    return value


def _parse_limit(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(f"--limit must be an integer, got '{raw}'")
    if value <= 0:
        raise ValueError(f"--limit must be a positive integer, got {value}")
    return value


def _parse_format(raw: str) -> str:
    if raw not in _VALID_FORMATS:
        raise ValueError(
            f"--format must be one of {sorted(_VALID_FORMATS)}, got '{raw}'"
        )
    return raw


def parse_cli_args(argv: list[str]) -> dict:
    """Parse *argv* and return a validated options dictionary.

    Raises ValueError for any invalid, missing, or unknown input.
    """
    result: dict = {
        "input": None,
        "limit": _DEFAULT_LIMIT,
        "format": _DEFAULT_FORMAT,
        "dry_run": False,
    }

    skip_next = False
    for index, token in enumerate(argv):
        if skip_next:
            skip_next = False
            continue

        if token == "--input":
            result["input"] = _consume_value(token, index, argv)
            skip_next = True

        elif token == "--limit":
            raw = _consume_value(token, index, argv)
            result["limit"] = _parse_limit(raw)
            skip_next = True

        elif token == "--format":
            raw = _consume_value(token, index, argv)
            result["format"] = _parse_format(raw)
            skip_next = True

        elif token == "--dry-run":
            result["dry_run"] = True

        elif token.startswith("--"):
            raise ValueError(f"Unknown flag: '{token}'")

        else:
            raise ValueError(f"Unexpected argument: '{token}'")

    if result["input"] is None:
        raise ValueError("--input is required but was not provided")

    return result
