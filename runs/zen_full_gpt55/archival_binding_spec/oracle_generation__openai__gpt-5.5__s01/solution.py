from __future__ import annotations


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    bindings_ledger: dict[str, dict[str, str]] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        stripped_line = raw_line.strip()

        if not stripped_line:
            continue

        if stripped_line.startswith("#"):
            continue

        left_side, separator, raw_value = stripped_line.partition("=")
        if not separator:
            raise ValueError(
                f"Malformed archival field 'binding' on line {line_number}: missing '='"
            )

        raw_section, key_separator, raw_key = left_side.partition(".")
        if not key_separator:
            raise ValueError(
                f"Malformed archival field 'binding' on line {line_number}: missing '.'"
            )

        section = raw_section.strip()
        key = raw_key.strip()
        value = raw_value.strip()

        if not section:
            raise ValueError(
                f"Rejected archival field 'section' on line {line_number}: empty section name"
            )

        if not key:
            raise ValueError(
                f"Rejected archival field 'key' on line {line_number}: empty key"
            )

        if section not in bindings_ledger:
            bindings_ledger[section] = {}

        section_ledger = bindings_ledger[section]
        section_ledger[key] = value

    return bindings_ledger
