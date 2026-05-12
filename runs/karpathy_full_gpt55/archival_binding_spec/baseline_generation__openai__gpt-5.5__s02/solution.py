from __future__ import annotations


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse binding lines of the form "section.key=value".

    Empty lines and lines whose first non-whitespace character is "#" are ignored.
    Whitespace around section names, keys, and values is stripped.

    Raises:
        ValueError: If a non-empty, non-comment line is malformed, or if the
        section name or key is empty.
    """
    bindings: dict[str, dict[str, str]] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        stripped_line = raw_line.strip()

        if not stripped_line or stripped_line.startswith("#"):
            continue

        if "=" not in raw_line:
            raise ValueError(f"Malformed line {line_number}: missing '='")

        left, value = raw_line.split("=", 1)

        if "." not in left:
            raise ValueError(f"Malformed line {line_number}: missing '.'")

        section, key = left.split(".", 1)
        section = section.strip()
        key = key.strip()
        value = value.strip()

        if not section:
            raise ValueError(f"Malformed line {line_number}: empty section name")

        if not key:
            raise ValueError(f"Malformed line {line_number}: empty key")

        if section not in bindings:
            bindings[section] = {}

        bindings[section][key] = value

    return bindings
