def parse_cli_args(argv: list[str]) -> dict:
    result = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    known_flags = {"--input", "--limit", "--format", "--dry-run"}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if not arg.startswith("--"):
            raise ValueError(f"Unknown argument: {arg!r}")
        if arg not in known_flags:
            raise ValueError(f"Unknown flag: {arg!r}")

        if arg == "--dry-run":
            result["dry_run"] = True
            i += 1
        elif arg == "--input":
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise ValueError("--input requires a value")
            result["input"] = argv[i + 1]
            i += 2
        elif arg == "--limit":
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise ValueError("--limit requires a value")
            raw = argv[i + 1]
            try:
                val = int(raw)
            except ValueError:
                raise ValueError(f"--limit must be an integer, got {raw!r}")
            if val <= 0:
                raise ValueError(f"--limit must be a positive integer, got {val}")
            result["limit"] = val
            i += 2
        elif arg == "--format":
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise ValueError("--format requires a value")
            raw = argv[i + 1]
            if raw not in ("json", "csv"):
                raise ValueError(f"--format must be 'json' or 'csv', got {raw!r}")
            result["format"] = raw
            i += 2

    if result["input"] is None:
        raise ValueError("--input is required")

    return result
