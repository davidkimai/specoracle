"""
archival_binding_spec: parse_bindings and flatten_bindings implementation.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse a list of strings into a nested dict of {section: {key: value}}.

    Each non-empty, non-comment line must be in the form "section.key=value".
    Comments start with '#'. Whitespace around section, key, and value is stripped.

    Raises ValueError for malformed lines, empty section names, or empty keys.
    """
    result: dict[str, dict[str, str]] = {}

    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Must contain '='
        if '=' not in line:
            raise ValueError(
                f"Line {lineno}: malformed line (missing '='): {raw_line!r}"
            )

        # Split on the first '=' only
        left, value = line.split('=', 1)
        left = left.strip()
        value = value.strip()

        # Left side must contain '.'
        if '.' not in left:
            raise ValueError(
                f"Line {lineno}: malformed line (missing '.' in section.key): {raw_line!r}"
            )

        # Split on the first '.' only
        section, key = left.split('.', 1)
        section = section.strip()
        key = key.strip()

        if not section:
            raise ValueError(
                f"Line {lineno}: empty section name in line: {raw_line!r}"
            )

        if not key:
            raise ValueError(
                f"Line {lineno}: empty key in line: {raw_line!r}"
            )

        if section not in result:
            result[section] = {}

        result[section][key] = value

    return result


def flatten_bindings(bindings: dict[str, dict[str, str]]) -> list[str]:
    """
    Flatten a nested bindings dict into a list of "section.key=value" strings.

    Entries are returned in dictionary iteration order.
    """
    result: list[str] = []
    for section, pairs in bindings.items():
        for key, value in pairs.items():
            result.append(f"{section}.{key}={value}")
    return result
