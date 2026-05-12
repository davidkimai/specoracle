DEFAULT_LIMIT = 100
DEFAULT_FORMAT = "json"
VALID_FORMATS = {"json", "csv"}
VALUE_FLAGS = {"--input", "--limit", "--format"}


def parse_cli_args(argv: list[str]) -> dict:
    _validate_argv(argv)

    parsed = {
        "input": None,
        "limit": DEFAULT_LIMIT,
        "format": DEFAULT_FORMAT,
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

        if token in VALUE_FLAGS:
            _reject_duplicate(token, seen)
            value, index = _read_flag_value(argv, index, token)
            _apply_value(parsed, token, value)
            continue

        if token.startswith("--"):
            raise ValueError(f"unknown flag: {token}")

        raise ValueError(f"unexpected argument: {token}")

    if parsed["input"] is None:
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

    for index, value in enumerate(argv):
        if not isinstance(value, str):
            raise ValueError(f"argv[{index}] must be a string")


def _reject_duplicate(flag: str, seen: set[str]) -> None:
    if flag in seen:
        raise ValueError(f"duplicate flag: {flag}")
    seen.add(flag)


def _read_flag_value(argv: list[str], flag_index: int, flag: str) -> tuple[str, int]:
    value_index = flag_index + 1
    if value_index >= len(argv):
        raise ValueError(f"missing value for {flag}")

    value = argv[value_index]
    if value.startswith("--"):
        raise ValueError(f"missing value for {flag}")

    return value, value_index + 1


def _apply_value(parsed: dict, flag: str, value: str) -> None:
    if flag == "--input":
        if value == "":
            raise ValueError("invalid value for --input: must not be empty")
        parsed["input"] = value
        return

    if flag == "--limit":
        parsed["limit"] = _parse_positive_integer(value, flag)
        return

    if flag == "--format":
        if value not in VALID_FORMATS:
            raise ValueError("invalid value for --format: expected 'json' or 'csv'")
        parsed["format"] = value
        return

    raise ValueError(f"unknown flag: {flag}")


def _parse_positive_integer(value: str, flag: str) -> int:
    if not _is_ascii_decimal(value):
        raise ValueError(f"invalid value for {flag}: expected a positive integer")

    number = int(value)
    if number <= 0:
        raise ValueError(f"invalid value for {flag}: expected a positive integer")

    return number


def _is_ascii_decimal(value: str) -> bool:
    return value != "" and all("0" <= character <= "9" for character in value)
