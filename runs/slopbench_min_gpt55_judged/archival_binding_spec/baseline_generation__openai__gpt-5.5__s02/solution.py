from __future__ import annotations


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise ValueError(f"Malformed line {line_number}: missing '='")

        left, value = line.split("=", 1)
        value = value.strip()

        if "." not in left:
            raise ValueError(f"Malformed line {line_number}: missing '.'")

        section, key = left.split(".", 1)
        section = section.strip()
        key = key.strip()

        if not section:
            raise ValueError(f"Malformed line {line_number}: empty section name")
        if not key:
            raise ValueError(f"Malformed line {line_number}: empty key")

        if section not in result:
            result[section] = {}
        result[section][key] = value

    return result
