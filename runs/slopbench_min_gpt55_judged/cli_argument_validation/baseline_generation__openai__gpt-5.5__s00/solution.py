from __future__ import annotations


def parse_cli_args(argv: list[str]) -> dict:
    if not isinstance(argv, list):
        raise ValueError("argv must be a list of strings")

    result = {
        "input": None,
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }

    requires_value = {"--input", "--limit", "--format"}
    boolean_flags = {"--dry-run"}
    supported_flags = requires_value | boolean_flags

    index = 0
    while index < len(argv):
        token = argv[index]

        if not isinstance(token, str):
            raise ValueError("all arguments must be strings")

        if token not in supported_flags:
            if token.startswith("-"):
                raise ValueError(f"unknown flag: {token}")
            raise ValueError(f"unexpected argument: {token}")

        if token in boolean_flags:
            result["dry_run"] = True
            index += 1
            continue

        if index + 1 >= len(argv):
            raise ValueError(f"missing value for {token}")

        value = argv[index + 1]
        if not isinstance(value, str):
            raise ValueError(f"missing value for {token}")

        if value.startswith("--"):
            raise ValueError(f"missing value for {token}")

        if token == "--input":
            if value == "":
                raise ValueError("invalid value for --input")
            result["input"] = value

        elif token == "--limit":
            if not value.isdigit():
                raise ValueError("invalid value for --limit")
            limit = int(value)
            if limit <= 0:
                raise ValueError("invalid value for --limit")
            result["limit"] = limit

        elif token == "--format":
            if value not in {"json", "csv"}:
                raise ValueError("invalid value for --format")
            result["format"] = value

        index += 2

    if result["input"] is None:
        raise ValueError("missing required flag: --input")

    return {
        "input": result["input"],
        "limit": result["limit"],
        "format": result["format"],
        "dry_run": result["dry_run"],
    }
