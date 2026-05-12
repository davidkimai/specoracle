def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    bindings_ledger: dict[str, dict[str, str]] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        stripped_line = raw_line.strip()

        if not stripped_line:
            continue

        if stripped_line.startswith("#"):
            continue

        name_part, separator, value_part = stripped_line.partition("=")
        if separator != "=":
            raise ValueError(
                f"malformed archival field 'section.key=value' on line {line_number}"
            )

        section_key_part = name_part.strip()
        value = value_part.strip()

        section_part, dot_separator, key_part = section_key_part.partition(".")
        if dot_separator != ".":
            raise ValueError(
                f"malformed archival field 'section.key' on line {line_number}"
            )

        section = section_part.strip()
        key = key_part.strip()

        if not section:
            raise ValueError(f"empty archival field 'section' on line {line_number}")

        if not key:
            raise ValueError(f"empty archival field 'key' on line {line_number}")

        if section not in bindings_ledger:
            bindings_ledger[section] = {}

        section_ledger = bindings_ledger[section]
        section_ledger[key] = value

    return bindings_ledger
