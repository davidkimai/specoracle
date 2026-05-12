def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """Parse archival binding lines of the form 'section.key=value'."""
    bindings_ledger: dict[str, dict[str, str]] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        stripped_line = raw_line.strip()

        if stripped_line == "":
            continue

        if stripped_line.startswith("#"):
            continue

        if "=" not in stripped_line:
            raise ValueError(
                f"malformed archival binding line at line {line_number}: missing '='"
            )

        name_part, value_part = stripped_line.split("=", 1)

        if "." not in name_part:
            raise ValueError(
                f"malformed archival binding line at line {line_number}: missing '.'"
            )

        section_part, key_part = name_part.split(".", 1)

        section_name = section_part.strip()
        key_name = key_part.strip()
        value_text = value_part.strip()

        if section_name == "":
            raise ValueError(f"empty archival section at line {line_number}")

        if key_name == "":
            raise ValueError(f"empty archival key at line {line_number}")

        if section_name not in bindings_ledger:
            bindings_ledger[section_name] = {}

        section_ledger = bindings_ledger[section_name]
        section_ledger[key_name] = value_text

    return bindings_ledger
