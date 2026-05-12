def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    section_ledger: dict[str, dict[str, str]] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        working_line = raw_line.strip()

        if working_line == "":
            continue

        if working_line.startswith("#"):
            continue

        if "=" not in working_line:
            raise ValueError(
                f"malformed archival binding line at line {line_number}: missing '='"
            )

        name_part, value_part = working_line.split("=", 1)
        name_part = name_part.strip()
        value = value_part.strip()

        if "." not in name_part:
            raise ValueError(
                f"malformed archival binding line at line {line_number}: missing section.key"
            )

        section_part, key_part = name_part.split(".", 1)
        section = section_part.strip()
        key = key_part.strip()

        if section == "":
            raise ValueError(f"empty archival section at line {line_number}")

        if key == "":
            raise ValueError(f"empty archival key at line {line_number}")

        if section not in section_ledger:
            section_ledger[section] = {}

        key_ledger = section_ledger[section]
        key_ledger[key] = value

    return section_ledger
