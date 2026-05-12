from __future__ import annotations

from typing import Any


_VALID_FORMATS = {"json", "csv"}
_VALUE_FLAGS = {"--input", "--limit", "--format"}
_BOOLEAN_FLAGS = {"--dry-run"}
_ALL_FLAGS = _VALUE_FLAGS | _BOOLEAN_FLAGS


def parse_cli_args(argv: list[str]) -> dict[str, Any]:
    """
    Parse and validate command-line arguments.

    Supported flags:
      --input PATH     required
      --limit N        optional, defaults to 100; must be a positive integer
      --format VALUE   optional, defaults to "json"; must be "json" or "csv"
      --dry-run        optional boolean flag

    Raises:
        ValueError: for missing required flags, unknown flags, missing values,
                    or invalid values.
    """
    if not isinstance(argv, list):
        raise ValueError("argv must be a list of strings")

    result: dict[str, Any] = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    seen_flags: set[str] = set()
    i = 0

    while i < len(argv):
        arg = argv[i]

        if not isinstance(arg, str):
            raise ValueError("argv must contain only strings")

        if arg == "--dry-run":
            if arg in seen_flags:
                raise ValueError("duplicate flag: --dry-run")
            seen_flags.add(arg)
            result["dry_run"] = True
            i += 1
            continue

        if arg in _VALUE_FLAGS:
            if arg in seen_flags:
                raise ValueError(f"duplicate flag: {arg}")
            seen_flags.add(arg)

            if i + 1 >= len(argv):
                raise ValueError(f"missing value for {arg}")

            value = argv[i + 1]
            if not isinstance(value, str):
                raise ValueError("argv must contain only strings")
            if value.startswith("--"):
                raise ValueError(f"missing value for {arg}")

            if arg == "--input":
                if value == "":
                    raise ValueError("invalid value for --input")
                result["input"] = value
            elif arg == "--limit":
                result["limit"] = _parse_positive_int(value)
            elif arg == "--format":
                if value not in _VALID_FORMATS:
                    raise ValueError("invalid value for --format")
                result["format"] = value

            i += 2
            continue

        if arg.startswith("--"):
            raise ValueError(f"unknown flag: {arg}")

        raise ValueError(f"unexpected argument: {arg}")

    if result["input"] is None:
        raise ValueError("missing required flag: --input")

    return {
        "input": result["input"],
        "limit": result["limit"],
        "format": result["format"],
        "dry_run": result["dry_run"],
    }


def _parse_positive_int(value: str) -> int:
    if not value.isdecimal():
        raise ValueError("invalid value for --limit")

    parsed = int(value)
    if parsed <= 0:
        raise ValueError("invalid value for --limit")

    return parsed
