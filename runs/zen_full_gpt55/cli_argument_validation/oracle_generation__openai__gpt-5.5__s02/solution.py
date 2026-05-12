_DEFAULT_LIMIT = 100
_DEFAULT_FORMAT = "json"
_ALLOWED_FORMATS = {"json", "csv"}
_VALUE_FLAGS = {"--input", "--limit", "--format"}
_BOOLEAN_FLAGS = {"--dry-run"}
_ALL_FLAGS = _VALUE_FLAGS | _BOOLEAN_FLAGS


def parse_cli_args(argv: list[str]) -> dict:
    _validate_argv(argv)

    result = {
        "input": None,
        "limit": _DEFAULT_LIMIT,
        "format": _DEFAULT_FORMAT,
        "dry_run": False,
    }
    seen_flags: set[str] = set()

    index = 0
    while index < len(argv):
        token = argv[index]

        if token == "--dry-run":
            _mark_seen(token, seen_flags)
            result["dry_run"] = True
            index += 1
            continue

        if token in _VALUE_FLAGS:
            _mark_seen(token, seen_flags)
            value = _read_flag_value(argv, index)
            _apply_value(result, token, value)
            index += 2
            continue

        if token.startswith("-"):
            raise ValueError(f"Unknown flag: {token}")

        raise ValueError(f"Unexpected argument: {token}")

    if result["input"] is None:
        raise ValueError("Missing required flag: --input")

    return result


def _validate_argv(argv: list[str]) -> None:
    if not isinstance(argv, list):
        raise ValueError("argv must be a list of strings")

    for index, token in enumerate(argv):
        if not isinstance(token, str):
            raise ValueError(f"argv[{index}] must be a string")


def _mark_seen(flag: str, seen_flags: set[str]) -> None:
    if flag in seen_flags:
        raise ValueError(f"Duplicate flag: {flag}")
    seen_flags.add(flag)


def _read_flag_value(argv: list[str], flag_index: int) -> str:
    flag = argv[flag_index]
    value_index = flag_index + 1

    if value_index >= len(argv):
        raise ValueError(f"Missing value for {flag}")

    value = argv[value_index]
    if value.startswith("--"):
        raise ValueError(f"Missing value for {flag}")

    return value


def _apply_value(result: dict, flag: str, value: str) -> None:
    if flag == "--input":
        result["input"] = value
        return

    if flag == "--limit":
        result["limit"] = _parse_limit(value)
        return

    if flag == "--format":
        result["format"] = _parse_format(value)
        return

    raise ValueError(f"Unknown flag: {flag}")


def _parse_limit(value: str) -> int:
    try:
        limit = int(value, 10)
    except ValueError as error:
        raise ValueError("--limit must be a positive integer") from error

    if limit <= 0:
        raise ValueError("--limit must be a positive integer")

    return limit


def _parse_format(value: str) -> str:
    if value not in _ALLOWED_FORMATS:
        raise ValueError('--format must be "json" or "csv"')

    return value
