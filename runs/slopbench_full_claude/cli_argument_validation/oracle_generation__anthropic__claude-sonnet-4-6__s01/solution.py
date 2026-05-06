"""cli_argument_validation.py

Parse and validate a fixed set of CLI flags without calling sys.exit.
"""

from __future__ import annotations

_VALID_FORMATS = {"json", "csv"}
_DEFAULT_LIMIT = 100
_DEFAULT_FORMAT = "json"


def _consume_value(flag: str, argv: list[str], index: int) -> str:
    """Return the value token that follows *flag* at *index* in *argv*."""
    next_index = index + 1
    if next_index >= len(argv):
        raise ValueError(f"{flag} requires a value but none was provided")
    value = argv[next_index]
    if value.startswith("--"):
        raise ValueError(f"{flag} requires a value but got another flag: {value!r}")
    return value


def _parse_limit(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(f"--limit must be an integer, got {raw!r}")
    if value <= 0:
        raise ValueError(f"--limit must be a positive integer, got {value}")
    return value


def _parse_format(raw: str) -> str:
    if raw not in _VALID_FORMATS:
        raise ValueError(
            f"--format must be one of {sorted(_VALID_FORMATS)}, got {raw!r}"
        )
    return raw


def parse_cli_args(argv: list[str]) -> dict:
    """Parse *argv* and return a validated options dict.

    Raises ValueError for any validation failure.
    """
    result: dict = {
        "input": None,
        "limit": _DEFAULT_LIMIT,
        "format": _DEFAULT_FORMAT,
        "dry_run": False,
    }

    known_flags = {"--input", "--limit", "--format", "--dry-run"}

    index = 0
    while index < len(argv):
        token = argv[index]

        if token == "--input":
            result["input"] = _consume_value("--input", argv, index)
            index += 2
        elif token == "--limit":
            raw = _consume_value("--limit", argv, index)
            result["limit"] = _parse_limit(raw)
            index += 2
        elif token == "--format":
            raw = _consume_value("--format", argv, index)
            result["format"] = _parse_format(raw)
            index += 2
        elif token == "--dry-run":
            result["dry_run"] = True
            index += 1
        else:
            raise ValueError(
                f"Unknown flag or unexpected argument: {token!r}. "
                f"Supported flags: {sorted(known_flags)}"
            )

    if result["input"] is None:
        raise ValueError("--input is required but was not provided")

    return result
