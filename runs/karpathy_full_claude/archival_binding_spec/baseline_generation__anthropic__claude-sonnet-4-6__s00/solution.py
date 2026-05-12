def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if '=' not in stripped:
            raise ValueError(f"Malformed line (missing '='): {line!r}")
        eq_pos = stripped.index('=')
        lhs = stripped[:eq_pos]
        value = stripped[eq_pos + 1:].strip()
        if '.' not in lhs:
            raise ValueError(f"Malformed line (missing '.' in key): {line!r}")
        dot_pos = lhs.index('.')
        section = lhs[:dot_pos].strip()
        key = lhs[dot_pos + 1:].strip()
        if not section:
            raise ValueError(f"Empty section name in line: {line!r}")
        if not key:
            raise ValueError(f"Empty key in line: {line!r}")
        if section not in result:
            result[section] = {}
        result[section][key] = value
    return result
