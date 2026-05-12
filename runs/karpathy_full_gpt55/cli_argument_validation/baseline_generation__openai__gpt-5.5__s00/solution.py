def parse_cli_args(argv: list[str]) -> dict:
    if not isinstance(argv, list):
        raise ValueError("argv must be a list of strings")

    result = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }
    seen = set()

    i = 0
    while i < len(argv):
        token = argv[i]

        if not isinstance(token, str):
            raise ValueError("argv must contain only strings")

        if token == "--input":
            if "input" in seen:
                raise ValueError("duplicate flag: --input")
            if i + 1 >= len(argv) or not isinstance(argv[i + 1], str) or argv[i + 1].startswith("--"):
                raise ValueError("missing value for --input")
            value = argv[i + 1]
            if value == "":
                raise ValueError("invalid value for --input")
            result["input"] = value
            seen.add("input")
            i += 2

        elif token == "--limit":
            if "limit" in seen:
                raise ValueError("duplicate flag: --limit")
            if i + 1 >= len(argv) or not isinstance(argv[i + 1], str) or argv[i + 1].startswith("--"):
                raise ValueError("missing value for --limit")
            value = argv[i + 1]
            if not value.isdigit():
                raise ValueError("invalid value for --limit")
            limit = int(value)
            if limit <= 0:
                raise ValueError("invalid value for --limit")
            result["limit"] = limit
            seen.add("limit")
            i += 2

        elif token == "--format":
            if "format" in seen:
                raise ValueError("duplicate flag: --format")
            if i + 1 >= len(argv) or not isinstance(argv[i + 1], str) or argv[i + 1].startswith("--"):
                raise ValueError("missing value for --format")
            value = argv[i + 1]
            if value not in ("json", "csv"):
                raise ValueError("invalid value for --format")
            result["format"] = value
            seen.add("format")
            i += 2

        elif token == "--dry-run":
            if "dry_run" in seen:
                raise ValueError("duplicate flag: --dry-run")
            result["dry_run"] = True
            seen.add("dry_run")
            i += 1

        elif token.startswith("--"):
            raise ValueError(f"unknown flag: {token}")

        else:
            raise ValueError(f"unknown argument: {token}")

    if result["input"] is None:
        raise ValueError("missing required flag: --input")

    return result
