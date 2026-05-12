_ALLOWED_FORMATS = {"json", "csv"}


def parse_cli_args(argv: list[str]) -> dict:
    if not isinstance(argv, list):
        raise ValueError("argv must be a list of strings")

    for argument in argv:
        if not isinstance(argument, str):
            raise ValueError("argv must contain only strings")

    values = {
        "limit": 100,
        "format": "json",
        "dry_run": False,
    }
    seen = set()

    index = 0
    while index < len(argv):
        flag = argv[index]

        if flag == "--input":
            _reject_duplicate(flag, seen)
            values["input"] = _read_value(argv, index, flag)
            index += 2
            continue

        if flag == "--limit":
            _reject_duplicate(flag, seen)
            values["limit"] = _parse_positive_integer(_read_value(argv, index, flag))
            index += 2
            continue

        if flag == "--format":
            _reject_duplicate(flag, seen)
            values["format"] = _parse_format(_read_value(argv, index, flag))
            index += 2
            continue

        if flag == "--dry-run":
            _reject_duplicate(flag, seen)
            values["dry_run"] = True
            index += 1
            continue

        if flag.startswith("--"):
            raise ValueError(f"unknown flag: {flag}")

        raise ValueError(f"unknown argument: {flag}")

    if "input" not in values:
        raise ValueError("missing required flag: --input")

    return {
        "input": values["input"],
        "limit": values["limit"],
        "format": values["format"],
        "dry_run": values["dry_run"],
    }


def _reject_duplicate(flag: str, seen: set[str]) -> None:
    if flag in seen:
        raise ValueError(f"duplicate flag: {flag}")
    seen.add(flag)


def _read_value(argv: list[str], flag_index: int, flag: str) -> str:
    value_index = flag_index + 1
    if value_index >= len(argv):
        raise ValueError(f"missing value for {flag}")

    value = argv[value_index]
    if value.startswith("--"):
        raise ValueError(f"missing value for {flag}")

    return value


def _parse_positive_integer(value: str) -> int:
    if not _is_ascii_integer(value):
        raise ValueError("--limit must be a positive integer")

    number = int(value)
    if number <= 0:
        raise ValueError("--limit must be a positive integer")

    return number


def _is_ascii_integer(value: str) -> bool:
    if not value:
        return False
    return all("0" <= character <= "9" for character in value)


def _parse_format(value: str) -> str:
    if value not in _ALLOWED_FORMATS:
        raise ValueError('--format must be "json" or "csv"')
    return value
