from __future__ import annotations


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse binding lines of the form "section.key=value".

    Empty lines and lines whose first non-whitespace character is "#" are ignored.
    Whitespace around section, key, and value is stripped.

    Raises:
        ValueError: If a non-empty, non-comment line is malformed, has an empty
        section name, or has an empty key.
    """
    result: dict[str, dict[str, str]] = {}

    for line_number, line in enumerate(lines, start=1):
        stripped_line = line.strip()

        if not stripped_line or stripped_line.startswith("#"):
            continue

        if "=" not in stripped_line:
            raise ValueError(f"Malformed line {line_number}: missing '='")

        left, value = stripped_line.split("=", 1)

        if "." not in left:
            raise ValueError(f"Malformed line {line_number}: missing '.' before '='")

        section, key = left.split(".", 1)

        section = section.strip()
        key = key.strip()
        value = value.strip()

        if not section:
            raise ValueError(f"Malformed line {line_number}: empty section name")

        if not key:
            raise ValueError(f"Malformed line {line_number}: empty key")

        if section not in result:
            result[section] = {}

        result[section][key] = value

    return result
