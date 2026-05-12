from __future__ import annotations


def parse_cli_args(argv: list[str]) -> dict:
    """
    Parse command-line arguments.

    Supported flags:
      --input PATH   Required.
      --limit N      Optional positive integer, defaults to 100.
      --format VALUE Optional, "json" or "csv", defaults to "json".
      --dry-run      Optional boolean flag.

    Raises:
        ValueError: for missing required flags, unknown flags, missing values,
                    unexpected positional arguments, or invalid values.
    """
    result = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    i = 0
    while i < len(argv):
        arg = argv[i]

        if arg == "--dry-run":
            result["dry_run"] = True
            i += 1
            continue

        if arg in {"--input", "--limit", "--format"}:
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise ValueError(f"missing value for {arg}")

            value = argv[i + 1]

            if arg == "--input":
                if value == "":
                    raise ValueError("invalid value for --input")
                result["input"] = value

            elif arg == "--limit":
                if not value or not all("0" <= ch <= "9" for ch in value):
                    raise ValueError("invalid value for --limit")
                limit = int(value)
                if limit <= 0:
                    raise ValueError("invalid value for --limit")
                result["limit"] = limit

            elif arg == "--format":
                if value not in {"json", "csv"}:
                    raise ValueError("invalid value for --format")
                result["format"] = value

            i += 2
            continue

        if arg.startswith("-"):
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
