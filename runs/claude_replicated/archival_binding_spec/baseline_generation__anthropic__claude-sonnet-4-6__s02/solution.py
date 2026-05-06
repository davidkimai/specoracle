"""
archival_binding_spec module
Provides parse_bindings for parsing section.key=value configuration lines.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse a list of configuration lines into a nested dictionary.

    Each non-empty, non-comment line must be in the format "section.key=value".
    Comments start with '#'. Whitespace around section, key, and value is stripped.

    Args:
        lines: List of strings to parse.

    Returns:
        An insertion-ordered nested dictionary mapping section names to
        dictionaries of key/value pairs.

    Raises:
        ValueError: For malformed lines, empty section names, or empty keys.
    """
    result: dict[str, dict[str, str]] = {}

    for lineno, raw_line in enumerate(lines, start=1):
        # Strip leading/trailing whitespace from the line
        line = raw_line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip comment lines
        if line.startswith('#'):
            continue

        # Check for '=' separator
        if '=' not in line:
            raise ValueError(
                f"Line {lineno}: malformed line (missing '='): {raw_line!r}"
            )

        # Split on the first '=' only
        lhs, value = line.split('=', 1)
        lhs = lhs.strip()
        value = value.strip()

        # Check for '.' separator in lhs
        if '.' not in lhs:
            raise ValueError(
                f"Line {lineno}: malformed line (missing '.' in section.key): {raw_line!r}"
            )

        # Split on the first '.' only
        section, key = lhs.split('.', 1)
        section = section.strip()
        key = key.strip()

        # Validate section and key are non-empty
        if not section:
            raise ValueError(
                f"Line {lineno}: empty section name in line: {raw_line!r}"
            )

        if not key:
            raise ValueError(
                f"Line {lineno}: empty key name in line: {raw_line!r}"
            )

        # Insert into result, preserving insertion order
        if section not in result:
            result[section] = {}

        result[section][key] = value

    return result
