from __future__ import annotations


def parse_cli_args(argv: list[str]) -> dict:
    _validate_argv(argv)

    parsed = {
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }
    seen_flags: set[str] = set()

    index = 0
    while index < len(argv):
        token = argv[index]

        if token == "--dry-run":
            _reject_duplicate(seen_flags, token)
            parsed["dry_run"] = True
            index += 1
            continue

        if token in {"--input", "--limit", "--format"}:
            _reject_duplicate(seen_flags, token)
            value = _read_flag_value(argv, index, token)
            _apply_value(parsed, token, value)
            index += 2
            continue

        if token.startswith("--"):
            raise ValueError(f"unknown flag: {token}")

        raise ValueError(f"unexpected argument: {token}")

    if "input" not in parsed:
        raise ValueError("missing required flag: --input")

    return parsed


def _validate_argv(argv: list[str]) -> None:
    if not isinstance(argv, list):
        raise ValueError("argv must be a list of strings")

    for item in argv:
        if not isinstance(item, str):
            raise ValueError("argv must be a list of strings")


def _reject_duplicate(seen_flags: set[str], flag: str) -> None:
    if flag in seen_flags:
        raise ValueError(f"duplicate flag: {flag}")

    seen_flags.add(flag)


def _read_flag_value(argv: list[str], flag_index: int, flag: str) -> str:
    value_index = flag_index + 1

    if value_index >= len(argv):
        raise ValueError(f"missing value for {flag}")

    value = argv[value_index]
    if value.startswith("--"):
        raise ValueError(f"missing value for {flag}")

    return value


def _apply_value(parsed: dict, flag: str, value: str) -> None:
    if flag == "--input":
        parsed["input"] = value
        return

    if flag == "--limit":
        parsed["limit"] = _parse_limit(value)
        return

    if flag == "--format":
        parsed["format"] = _parse_format(value)
        return

    raise ValueError(f"unknown flag: {flag}")


def _parse_limit(value: str) -> int:
    if not _is_ascii_integer(value):
        raise ValueError("--limit must be a positive integer")

    limit = int(value)
    if limit <= 0:
        raise ValueError("--limit must be a positive integer")

    return limit


def _is_ascii_integer(value: str) -> bool:
    if value == "":
        return False

    return all("0" <= character <= "9" for character in value)


def _parse_format(value: str) -> str:
    if value not in {"json", "csv"}:
        raise ValueError('--format must be "json" or "csv"')

    return value
