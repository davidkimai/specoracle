from typing import Any


def parse_cli_args(argv: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    input_path: str | None = None
    i = 0

    while i < len(argv):
        arg = argv[i]

        if arg == "--input":
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise ValueError("Missing value for --input")
            input_path = argv[i + 1]
            i += 2

        elif arg == "--limit":
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise ValueError("Missing value for --limit")
            value = argv[i + 1]
            if not value.isdigit():
                raise ValueError("--limit must be a positive integer")
            limit = int(value)
            if limit <= 0:
                raise ValueError("--limit must be a positive integer")
            result["limit"] = limit
            i += 2

        elif arg == "--format":
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise ValueError("Missing value for --format")
            value = argv[i + 1]
            if value not in {"json", "csv"}:
                raise ValueError('--format must be "json" or "csv"')
            result["format"] = value
            i += 2

        elif arg == "--dry-run":
            result["dry_run"] = True
            i += 1

        elif arg.startswith("--"):
            raise ValueError(f"Unknown flag: {arg}")

        else:
            raise ValueError(f"Unknown argument: {arg}")

    if input_path is None:
        raise ValueError("Missing required flag: --input")

    result["input"] = input_path
    return result
