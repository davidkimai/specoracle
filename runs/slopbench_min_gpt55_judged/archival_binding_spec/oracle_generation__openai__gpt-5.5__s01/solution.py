from __future__ import annotations


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    bindings_ledger: dict[str, dict[str, str]] = {}

    for line_number, original_line in enumerate(lines, start=1):
        stripped_line = original_line.strip()

        if not stripped_line:
            continue

        if stripped_line.startswith("#"):
            continue

        assignment_separator_index = original_line.find("=")
        if assignment_separator_index == -1:
            raise ValueError(
                f"malformed archival line at line {line_number}: "
                "missing '=' for archival field 'section.key=value'"
            )

        field_name_text = original_line[:assignment_separator_index]
        field_value_text = original_line[assignment_separator_index + 1 :]

        path_separator_index = field_name_text.find(".")
        if path_separator_index == -1:
            raise ValueError(
                f"malformed archival line at line {line_number}: "
                "missing '.' for archival field 'section.key'"
            )

        section_text = field_name_text[:path_separator_index]
        key_text = field_name_text[path_separator_index + 1 :]

        section = section_text.strip()
        key = key_text.strip()
        value = field_value_text.strip()

        if not section:
            raise ValueError(
                f"empty archival field 'section' at line {line_number}"
            )

        if not key:
            raise ValueError(
                f"empty archival field 'key' at line {line_number}"
            )

        section_ledger = bindings_ledger.get(section)
        if section_ledger is None:
            section_ledger = {}
            bindings_ledger[section] = section_ledger

        section_ledger[key] = value

    return bindings_ledger
