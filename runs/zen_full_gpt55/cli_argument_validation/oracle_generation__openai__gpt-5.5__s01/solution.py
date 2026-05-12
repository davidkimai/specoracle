from __future__ import annotations


_ALLOWED_FORMATS = {"json", "csv"}
_VALUE_FLAGS = {"--input", "--limit", "--format"}
_BOOLEAN_FLAGS = {"--dry-run"}
_ALL_FLAGS = _VALUE_FLAGS | _BOOLEAN_FLAGS


def parse_cli_args(argv: list[str]) -> dict:
    _validate_argv(argv)

    input_path: str | None = None
    limit = 100
    output_format = "json"
    dry_run = False
    seen_flags: set[str] = set()

    index = 0
    while index < len(argv):
        token = argv[index]

        if token not in _ALL_FLAGS:
            raise ValueError(f"unknown argument: {token}")

        if token in seen_flags:
            raise ValueError(f"duplicate flag: {token}")
        seen_flags.add(token)

        if token == "--dry-run":
            dry_run = True
            index += 1
            continue

        value = _read_flag_value(argv, index, token)

        if token == "--input":
            input_path = _parse_input_path(value)
        elif token == "--limit":
            limit = _parse_limit(value)
        elif token == "--format":
            output_format = _parse_format(value)

        index += 2

    if input_path is None:
        raise ValueError("missing required flag: --input")

    return {
        "input": input_path,
        "limit": limit,
        "format": output_format,
        "dry_run": dry_run,
    }


def _validate_argv(argv: list[str]) -> None:
    if not isinstance(argv, list):
        raise ValueError("argv must be a list of strings")

    for item in argv:
        if not isinstance(item, str):
            raise ValueError("argv must be a list of strings")


def _read_flag_value(argv: list[str], flag_index: int, flag: str) -> str:
    value_index = flag_index + 1

    if value_index >= len(argv):
        raise ValueError(f"missing value for {flag}")

    value = argv[value_index]
    if value in _ALL_FLAGS:
        raise ValueError(f"missing value for {flag}")

    return value


def _parse_input_path(value: str) -> str:
    if value == "":
        raise ValueError("invalid value for --input: path must not be empty")
    return value


def _parse_limit(value: str) -> int:
    try:
        limit = int(value, 10)
    except ValueError as error:
        raise ValueError("invalid value for --limit: must be a positive integer") from error

    if limit <= 0:
        raise ValueError("invalid value for --limit: must be a positive integer")

    return limit


def _parse_format(value: str) -> str:
    if value not in _ALLOWED_FORMATS:
        raise ValueError('invalid value for --format: must be "json" or "csv"')
    return value
