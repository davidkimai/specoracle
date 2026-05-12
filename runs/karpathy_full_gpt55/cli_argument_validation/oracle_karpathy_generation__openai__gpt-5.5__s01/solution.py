def parse_cli_args(argv: list[str]) -> dict:
    input_path = None
    limit = 100
    output_format = "json"
    dry_run = False

    i = 0
    while i < len(argv):
        arg = argv[i]

        if arg == "--dry-run":
            dry_run = True
            i += 1
            continue

        if arg in ("--input", "--limit", "--format"):
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise ValueError(f"missing value for {arg}")

            value = argv[i + 1]

            if arg == "--input":
                if value == "":
                    raise ValueError("invalid value for --input")
                input_path = value
            elif arg == "--limit":
                if not value.isascii() or not value.isdecimal():
                    raise ValueError("invalid value for --limit")
                limit = int(value)
                if limit <= 0:
                    raise ValueError("invalid value for --limit")
            else:
                if value not in ("json", "csv"):
                    raise ValueError("invalid value for --format")
                output_format = value

            i += 2
            continue

        if arg.startswith("--"):
            raise ValueError(f"unknown flag: {arg}")

        raise ValueError(f"unknown argument: {arg}")

    if input_path is None:
        raise ValueError("missing required flag: --input")

    return {
        "input": input_path,
        "limit": limit,
        "format": output_format,
        "dry_run": dry_run,
    }
