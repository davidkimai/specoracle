def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            raise ValueError(
                f"Line {lineno}: malformed binding (missing '='): {raw_line!r}"
            )
        lhs, _, value = line.partition('=')
        value = value.strip()
        if '.' not in lhs:
            raise ValueError(
                f"Line {lineno}: malformed binding (missing '.' in key): {raw_line!r}"
            )
        section_part, _, key_part = lhs.partition('.')
        section = section_part.strip()
        key = key_part.strip()
        if not section:
            raise ValueError(
                f"Line {lineno}: empty section name in binding: {raw_line!r}"
            )
        if not key:
            raise ValueError(
                f"Line {lineno}: empty key in binding: {raw_line!r}"
            )
        if section not in result:
            result[section] = {}
        result[section][key] = value
    return result
