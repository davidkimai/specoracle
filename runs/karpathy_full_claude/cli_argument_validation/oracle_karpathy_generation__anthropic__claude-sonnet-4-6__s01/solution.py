def parse_cli_args(argv: list) -> dict:
    result = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    known_flags = {"--input", "--limit", "--format", "--dry-run"}
    value_flags = {"--input", "--limit", "--format"}

    i = 0
    while i < len(argv):
        token = argv[i]
        if not token.startswith("--"):
            raise ValueError(f"Unknown argument: {token!r}")
        if token not in known_flags:
            raise ValueError(f"Unknown flag: {token!r}")

        if token == "--dry-run":
            result["dry_run"] = True
            i += 1
            continue

        # token requires a value
        if i + 1 >= len(argv):
            raise ValueError(f"Missing value for flag {token!r}")
        value = argv[i + 1]
        if value.startswith("--"):
            raise ValueError(f"Missing value for flag {token!r}")

        if token == "--input":
            result["input"] = value
        elif token == "--limit":
            try:
                n = int(value)
            except ValueError:
                raise ValueError(f"--limit must be an integer, got {value!r}")
            if n <= 0:
                raise ValueError(f"--limit must be a positive integer, got {n}")
            result["limit"] = n
        elif token == "--format":
            if value not in ("json", "csv"):
                raise ValueError(f"--format must be 'json' or 'csv', got {value!r}")
            result["format"] = value

        i += 2

    if result["input"] is None:
        raise ValueError("Missing required flag: --input")

    return result
