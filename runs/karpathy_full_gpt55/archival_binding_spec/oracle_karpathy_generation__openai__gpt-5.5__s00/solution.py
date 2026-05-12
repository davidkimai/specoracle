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
                f"malformed archival line at line {line_number}: missing '='"
            )

        name_part, value_part = stripped_line.split("=", 1)
        name_part = name_part.strip()
        value = value_part.strip()

        if "." not in name_part:
            raise ValueError(
                f"malformed archival line at line {line_number}: missing section.key"
            )

        section_part, key_part = name_part.split(".", 1)
        section = section_part.strip()
        key = key_part.strip()

        if section == "":
            raise ValueError(
                f"empty archival section at line {line_number}"
            )

        if key == "":
            raise ValueError(
                f"empty archival key at line {line_number}"
            )

        if section not in bindings_ledger:
            section_ledger: dict[str, str] = {}
            bindings_ledger[section] = section_ledger

        bindings_ledger[section][key] = value

    return bindings_ledger
