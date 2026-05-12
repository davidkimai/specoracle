def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    bindings_ledger: dict[str, dict[str, str]] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        visible_line = raw_line.strip()

        if visible_line == "":
            continue

        if visible_line.startswith("#"):
            continue

        if "=" not in visible_line:
            raise ValueError(
                f"malformed archival line at line {line_number}: missing '='"
            )

        left_text, value_text = visible_line.split("=", 1)

        if "." not in left_text:
            raise ValueError(
                f"malformed archival line at line {line_number}: missing section.key"
            )

        section_text, key_text = left_text.split(".", 1)

        section = section_text.strip()
        key = key_text.strip()
        value = value_text.strip()

        if section == "":
            raise ValueError(f"empty archival section at line {line_number}")

        if key == "":
            raise ValueError(f"empty archival key at line {line_number}")

        section_ledger = bindings_ledger.get(section)
        if section_ledger is None:
            section_ledger = {}
            bindings_ledger[section] = section_ledger

        section_ledger[key] = value

    return bindings_ledger
