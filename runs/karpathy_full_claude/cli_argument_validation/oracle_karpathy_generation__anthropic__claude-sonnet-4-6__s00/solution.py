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
            continue

        # All remaining flags require a value
        if i + 1 >= len(argv):
            raise ValueError(f"Flag {arg!r} requires a value but none was provided")
        value = argv[i + 1]
        if value.startswith("--"):
            raise ValueError(f"Flag {arg!r} requires a value but got flag {value!r}")

        if arg == "--input":
            result["input"] = value
        elif arg == "--limit":
            try:
                limit = int(value)
            except ValueError:
                raise ValueError(f"--limit must be an integer, got {value!r}")
            if limit <= 0:
                raise ValueError(f"--limit must be a positive integer, got {limit}")
            result["limit"] = limit
        elif arg == "--format":
            if value not in ("json", "csv"):
                raise ValueError(f"--format must be 'json' or 'csv', got {value!r}")
            result["format"] = value

        i += 2

    if result["input"] is None:
        raise ValueError("--input is required but was not provided")

    return result
