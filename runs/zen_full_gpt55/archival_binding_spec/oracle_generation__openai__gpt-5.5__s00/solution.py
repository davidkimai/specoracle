from __future__ import annotations


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    bindings_ledger: dict[str, dict[str, str]] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        stripped_line = raw_line.strip()

        if not stripped_line:
            continue

        if stripped_line.startswith("#"):
            continue

        if "=" not in stripped_line:
            raise ValueError(
                f"malformed archival binding line at line {line_number}: "
                "expected 'section.key=value'"
            )

        field_path, raw_value = stripped_line.split("=", 1)
        field_path = field_path.strip()
        value = raw_value.strip()

        if "." not in field_path:
            raise ValueError(
                f"malformed archival binding line at line {line_number}: "
                "expected archival field 'section.key'"
            )

        raw_section, raw_key = field_path.split(".", 1)
        section = raw_section.strip()
        key = raw_key.strip()

        if not section:
            raise ValueError(
                f"empty archival field 'section' at line {line_number}"
            )

        if not key:
            raise ValueError(
                f"empty archival field 'key' at line {line_number}"
            )

        if section not in bindings_ledger:
            bindings_ledger[section] = {}

        section_ledger = bindings_ledger[section]
        section_ledger[key] = value

    return bindings_ledger
