def parse_cli_args(argv: list[str]) -> dict:
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

        if arg in ("--input", "--limit", "--format"):
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise ValueError(f"missing value for {arg}")

            value = argv[i + 1]

            if arg == "--input":
                result["input"] = value
            elif arg == "--limit":
                try:
                    limit = int(value)
                except ValueError as exc:
                    raise ValueError("invalid value for --limit") from exc
                if limit <= 0:
                    raise ValueError("invalid value for --limit")
                result["limit"] = limit
            else:
                if value not in ("json", "csv"):
                    raise ValueError("invalid value for --format")
                result["format"] = value

            i += 2
            continue

        raise ValueError(f"unknown flag: {arg}")

    if result["input"] is None:
        raise ValueError("missing required flag: --input")

    return result.copy()
