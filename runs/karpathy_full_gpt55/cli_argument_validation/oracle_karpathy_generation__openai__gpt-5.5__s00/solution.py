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

        if arg == "--input":
            i += 1
            if i >= len(argv) or argv[i].startswith("--"):
                raise ValueError("missing value for --input")
            if argv[i] == "":
                raise ValueError("invalid value for --input")
            result["input"] = argv[i]

        elif arg == "--limit":
            i += 1
            if i >= len(argv) or argv[i].startswith("--"):
                raise ValueError("missing value for --limit")
            try:
                limit = int(argv[i])
            except ValueError as exc:
                raise ValueError("invalid value for --limit") from exc
            if limit <= 0:
                raise ValueError("invalid value for --limit")
            result["limit"] = limit

        elif arg == "--format":
            i += 1
            if i >= len(argv) or argv[i].startswith("--"):
                raise ValueError("missing value for --format")
            if argv[i] not in ("json", "csv"):
                raise ValueError("invalid value for --format")
            result["format"] = argv[i]

        elif arg == "--dry-run":
            result["dry_run"] = True

        else:
            raise ValueError(f"unknown flag: {arg}")

        i += 1

    if result["input"] is None:
        raise ValueError("missing required flag: --input")

    return result
