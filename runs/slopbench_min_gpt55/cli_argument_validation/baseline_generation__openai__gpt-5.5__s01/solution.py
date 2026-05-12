from __future__ import annotations


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parse supported command-line arguments.

    Supported flags:
      --input PATH       required
      --limit N          optional, defaults to 100, positive integer
      --format VALUE     optional, defaults to "json", must be "json" or "csv"
      --dry-run          optional boolean flag

    Raises ValueError for missing required flags, unknown flags, missing values,
    or invalid values.
    """
    input_value: str | None = None
    limit_value = 100
    format_value = "json"
    dry_run = False

    def require_value(index: int, flag: str) -> str:
        value_index = index + 1
        if value_index >= len(argv):
            raise ValueError(f"missing value for {flag}")

        value = argv[value_index]
        if not isinstance(value, str):
            raise ValueError(f"invalid value for {flag}")

        if value.startswith("--"):
            raise ValueError(f"missing value for {flag}")

        return value

    def parse_positive_int(value: str) -> int:
        if not value or not all("0" <= ch <= "9" for ch in value):
            raise ValueError("invalid value for --limit")

        parsed = int(value)
        if parsed <= 0:
            raise ValueError("invalid value for --limit")

        return parsed

    i = 0
    while i < len(argv):
        arg = argv[i]

        if not isinstance(arg, str):
            raise ValueError("invalid argument")

        if arg == "--input":
            input_value = require_value(i, "--input")
            i += 2
        elif arg == "--limit":
            limit_value = parse_positive_int(require_value(i, "--limit"))
            i += 2
        elif arg == "--format":
            candidate = require_value(i, "--format")
            if candidate not in {"json", "csv"}:
                raise ValueError("invalid value for --format")
            format_value = candidate
            i += 2
        elif arg == "--dry-run":
            dry_run = True
            i += 1
        else:
            raise ValueError(f"unknown flag: {arg}")

    if input_value is None:
        raise ValueError("missing required flag: --input")

    return {
        "input": input_value,
        "limit": limit_value,
        "format": format_value,
        "dry_run": dry_run,
    }
