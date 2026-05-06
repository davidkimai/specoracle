def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if '=' not in stripped:
            raise ValueError(
                f"Malformed line {line_number}: missing '=' in {line!r}"
            )
        left, _, value = stripped.partition('=')
        value = value.strip()
        if '.' not in left:
            raise ValueError(
                f"Malformed line {line_number}: missing '.' separator in {line!r}"
            )
        section, _, key = left.partition('.')
        section = section.strip()
        key = key.strip()
        if not section:
            raise ValueError(
                f"Malformed line {line_number}: empty section name in {line!r}"
            )
        if not key:
            raise ValueError(
                f"Malformed line {line_number}: empty key in {line!r}"
            )
        if section not in result:
            result[section] = {}
        result[section][key] = value
    return result
