from __future__ import annotations

_ALLOWED_FORMATS = {"json", "csv"}
_VALUE_FLAGS = {"--input", "--limit", "--format"}
_BOOLEAN_FLAGS = {"--dry-run"}
_KNOWN_FLAGS = _VALUE_FLAGS | _BOOLEAN_FLAGS


def parse_cli_args(argv: list[str]) -> dict:
    _validate_argv(argv)

    parsed: dict[str, object] = {
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }
    seen: set[str] = set()

    index = 0
    while index < len(argv):
        token = argv[index]

        if token == "--dry-run":
            _reject_duplicate(token, seen)
            parsed["dry_run"] = True
            index += 1
            continue

        if token in _VALUE_FLAGS:
            _reject_duplicate(token, seen)
            value = _read_flag_value(argv, index)
            _store_value(parsed, token, value)
            index += 2
            continue

        if token.startswith("--"):
            raise ValueError(f"unknown flag: {token}")

        raise ValueError(f"unexpected argument: {token}")

    if "input" not in parsed:
        raise ValueError("missing required flag: --input")

    return {
        "input": parsed["input"],
        "limit": parsed["limit"],
        "format": parsed["format"],
        "dry_run": parsed["dry_run"],
    }


def _validate_argv(argv: list[str]) -> None:
    if not isinstance(argv, list):
        raise ValueError("argv must be a list of strings")

    for index, item in enumerate(argv):
        if not isinstance(item, str):
            raise ValueError(f"argv[{index}] must be a string")


def _reject_duplicate(flag: str, seen: set[str]) -> None:
    if flag in seen:
        raise ValueError(f"duplicate flag: {flag}")
    seen.add(flag)


def _read_flag_value(argv: list[str], flag_index: int) -> str:
    flag = argv[flag_index]
    value_index = flag_index + 1

    if value_index >= len(argv):
        raise ValueError(f"missing value for {flag}")

    value = argv[value_index]
    if value.startswith("--"):
        raise ValueError(f"missing value for {flag}")

    return value


def _store_value(parsed: dict[str, object], flag: str, value: str) -> None:
    if flag == "--input":
        if value == "":
            raise ValueError("invalid value for --input")
        parsed["input"] = value
        return

    if flag == "--limit":
        parsed["limit"] = _parse_positive_integer(value, flag)
        return

    if flag == "--format":
        if value not in _ALLOWED_FORMATS:
            raise ValueError("invalid value for --format")
        parsed["format"] = value
        return

    raise ValueError(f"unknown flag: {flag}")


def _parse_positive_integer(value: str, flag: str) -> int:
    if not value.isdecimal():
        raise ValueError(f"invalid value for {flag}")

    number = int(value)
    if number <= 0:
        raise ValueError(f"invalid value for {flag}")

    return number
