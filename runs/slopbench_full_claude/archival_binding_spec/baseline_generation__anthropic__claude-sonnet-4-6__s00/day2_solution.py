"""
archival_binding_spec.py

Implements parse_bindings for parsing section.key=value configuration lines,
and flatten_bindings for serializing the nested dict back to a list of strings.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse a list of strings in "section.key=value" format into a nested dict.

    - Non-empty, non-comment lines must follow the "section.key=value" format.
    - Comments start with "#".
    - Whitespace around section, key, and value is stripped.
    - Returns an insertion-ordered nested dictionary: {section: {key: value}}.
    - Raises ValueError for malformed lines, empty section names, or empty keys.
    """
    result: dict[str, dict[str, str]] = {}

    for lineno, raw_line in enumerate(lines, start=1):
        # Strip leading/trailing whitespace from the whole line
        line = raw_line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Split on the first '=' to separate the left side from the value
        if "=" not in line:
            raise ValueError(
                f"Line {lineno}: malformed line (missing '='): {raw_line!r}"
            )

        left, _, value = line.partition("=")
        value = value.strip()

        # Split the left side on the first '.' to get section and key
        if "." not in left:
            raise ValueError(
                f"Line {lineno}: malformed line (missing '.' in key specification): {raw_line!r}"
            )

        section, _, key = left.partition(".")
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
    Serialize a nested bindings dict back into a list of "section.key=value" strings.

    Iterates in dictionary insertion order for both sections and keys.
    """
    result: list[str] = []
    for section, pairs in bindings.items():
        for key, value in pairs.items():
            result.append(f"{section}.{key}={value}")
    return result
