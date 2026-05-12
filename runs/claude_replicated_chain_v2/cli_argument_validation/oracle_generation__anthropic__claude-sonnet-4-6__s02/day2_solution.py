"""CLI argument validation module."""

from __future__ import annotations


def _parse_tokens(argv: list[str]) -> dict[str, str | bool | list[str]]:
    """Convert argv tokens into a raw flag-to-value mapping."""
    raw: dict[str, str | bool | list[str]] = {}
    i = 0
    while i < len(argv):
        token = argv[i]
        if not token.startswith("--"):
            raise ValueError(f"Unexpected argument: {token!r}")

        flag = token[2:]

        if flag == "dry-run":
            raw[flag] = True
            i += 1
            continue

        if flag == "tag":
            if i + 1 >= len(argv):
                raise ValueError(f"Flag --{flag} requires a value but none was provided")
            next_token = argv[i + 1]
            if next_token.startswith("--"):
                raise ValueError(f"Flag --{flag} requires a value but got flag {next_token!r}")
            tags_list = raw.setdefault("tag", [])
            tags_list.append(next_token)  # type: ignore[union-attr]
            i += 2
            continue

        if flag in ("input", "limit", "format"):
            if i + 1 >= len(argv):
                raise ValueError(f"Flag --{flag} requires a value but none was provided")
            next_token = argv[i + 1]
            if next_token.startswith("--"):
                raise ValueError(f"Flag --{flag} requires a value but got flag {next_token!r}")
            raw[flag] = next_token
            i += 2
            continue

        raise ValueError(f"Unknown flag: --{flag!r}")

    return raw


def _require_input(raw: dict) -> str:
    if "input" not in raw:
        raise ValueError("Required flag --input is missing")
    return str(raw["input"])


def _parse_limit(raw: dict) -> int:
    if "limit" not in raw:
        return 100
    value = raw["limit"]
    try:
        n = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"--limit must be an integer, got {value!r}")
    if n <= 0:
        raise ValueError(f"--limit must be a positive integer, got {n}")
    return n


def _parse_format(raw: dict) -> str:
    if "format" not in raw:
        return "json"
    value = raw["format"]
    allowed = ("json", "csv")
    if value not in allowed:
        raise ValueError(f"--format must be one of {allowed}, got {value!r}")
    return value


def _parse_dry_run(raw: dict) -> bool:
    return bool(raw.get("dry-run", False))


def _parse_tags(raw: dict) -> dict[str, str]:
    """Parse repeated --tag KEY=VALUE entries into a dictionary."""
    tags: dict[str, str] = {}
    entries: list[str] = raw.get("tag", [])  # type: ignore[assignment]
    for entry in entries:
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
    """Parse and validate CLI arguments.

    Args:
        argv: List of argument strings (excluding the program name).

    Returns:
        dict with keys: input (str), limit (int), format (str), dry_run (bool),
        tags (dict[str, str]).

    Raises:
        ValueError: For missing required flags, unknown flags, missing values,
                    or invalid values.
    """
    raw = _parse_tokens(argv)

    return {
        "input": _require_input(raw),
        "limit": _parse_limit(raw),
        "format": _parse_format(raw),
        "dry_run": _parse_dry_run(raw),
        "tags": _parse_tags(raw),
    }
