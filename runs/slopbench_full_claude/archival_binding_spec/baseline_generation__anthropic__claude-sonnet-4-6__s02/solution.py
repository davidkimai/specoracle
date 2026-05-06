"""
archival_binding_spec.py

Implements parse_bindings for parsing "section.key=value" formatted lines
into an insertion-ordered nested dictionary.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse a list of strings into a nested dictionary of sections to key/value pairs.

    Each non-empty, non-comment line must follow the format "section.key=value".
    Comments start with "#". Whitespace around section, key, and value is stripped.

    Args:
        lines: A list of strings to parse.

    Returns:
        An insertion-ordered nested dictionary mapping section names to
        dictionaries of key/value pairs.

    Raises:
        ValueError: For malformed lines, empty section names, or empty keys.
    """
    result: dict[str, dict[str, str]] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        # Strip leading/trailing whitespace from the line
        line = raw_line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip comment lines
        if line.startswith("#"):
            continue

        # Must contain '=' to separate key from value
        if "=" not in line:
            raise ValueError(
                f"Line {line_number}: Malformed line (missing '='): {raw_line!r}"
            )

        # Split on the first '=' only
        lhs, value = line.split("=", 1)
        lhs = lhs.strip()
        value = value.strip()

        # lhs must contain '.' to separate section from key
        if "." not in lhs:
            raise ValueError(
                f"Line {line_number}: Malformed line (missing '.' in section.key): {raw_line!r}"
            )

        # Split on the first '.' only
        section, key = lhs.split(".", 1)
        section = section.strip()
        key = key.strip()

        # Validate section name is not empty
        if not section:
            raise ValueError(
                f"Line {line_number}: Empty section name in line: {raw_line!r}"
            )

        # Validate key is not empty
        if not key:
            raise ValueError(
                f"Line {line_number}: Empty key in line: {raw_line!r}"
            )

        # Insert into result, preserving insertion order
        if section not in result:
            result[section] = {}

        result[section][key] = value

    return result
