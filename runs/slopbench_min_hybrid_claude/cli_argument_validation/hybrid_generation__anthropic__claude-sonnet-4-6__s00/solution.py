"""cli_argument_validation: parse and validate CLI arguments without sys.exit."""

from __future__ import annotations


_VALID_FORMATS = {"json", "csv"}
_DEFAULT_LIMIT = 100
_DEFAULT_FORMAT = "json"


def _parse_tokens(argv: list[str]) -> dict[str, str | bool]:
    """Convert a flat argv list into a raw {flag: value} mapping.

    Boolean flags map to True; value flags map to their string value.
    Raises ValueError for unknown flags or missing values.
    """
    known_flags = {"--input", "--limit", "--format", "--dry-run"}
    value_flags = {"--input", "--limit", "--format"}

    raw: dict[str, str | bool] = {}
    index = 0
    while index < len(argv):
        token = argv[index]
        if not token.startswith("--"):
            raise ValueError(f"Unexpected positional argument: {token!r}")
        if token not in known_flags:
            raise ValueError(f"Unknown flag: {token!r}")
        if token in value_flags:
            if index + 1 >= len(argv) or argv[index + 1].startswith("--"):
                raise ValueError(f"Flag {token!r} requires a value but none was given")
            raw[token] = argv[index + 1]
            index += 2
        else:
            raw[token] = True
            index += 1
    return raw


def _require_str(raw: dict, flag: str) -> str:
    if flag not in raw:
        raise ValueError(f"Required flag {flag!r} is missing")
    return str(raw[flag])


def _parse_limit(raw: dict) -> int:
    if "--limit" not in raw:
        return _DEFAULT_LIMIT
    value = raw["--limit"]
    try:
        limit = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"--limit must be an integer, got {value!r}")
    if limit <= 0:
        raise ValueError(f"--limit must be a positive integer, got {limit!r}")
    return limit


def _parse_format(raw: dict) -> str:
    if "--format" not in raw:
        return _DEFAULT_FORMAT
    fmt = str(raw["--format"])
    if fmt not in _VALID_FORMATS:
        raise ValueError(
            f"--format must be one of {sorted(_VALID_FORMATS)}, got {fmt!r}"
        )
    return fmt


def parse_cli_args(argv: list[str]) -> dict:
    """Parse and validate CLI arguments.

    Parameters
    ----------
    argv:
        Raw argument list (e.g. sys.argv[1:]).

    Returns
    -------
    dict with keys: input (str), limit (int), format (str), dry_run (bool).

    Raises
    ------
    ValueError
        For missing required flags, unknown flags, missing values, or invalid values.
    """
    raw = _parse_tokens(argv)

    input_path = _require_str(raw, "--input")
    limit = _parse_limit(raw)
    fmt = _parse_format(raw)
    dry_run = bool(raw.get("--dry-run", False))

    return {
        "input": input_path,
        "limit": limit,
        "format": fmt,
        "dry_run": dry_run,
    }
