def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    bindings_ledger: dict[str, dict[str, str]] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        stripped_line = raw_line.strip()

        if not stripped_line:
            continue

        if stripped_line.startswith("#"):
            continue

        equals_index = stripped_line.find("=")
        if equals_index == -1:
            raise ValueError(f"malformed archival binding line at line {line_number}: missing '='")

        left_text = stripped_line[:equals_index]
        value = stripped_line[equals_index + 1 :].strip()

        dot_index = left_text.find(".")
        if dot_index == -1:
            raise ValueError(f"malformed archival binding line at line {line_number}: missing section.key")

        section = left_text[:dot_index].strip()
        key = left_text[dot_index + 1 :].strip()

        if section == "":
            raise ValueError(f"empty archival section name at line {line_number}")

        if key == "":
            raise ValueError(f"empty archival key at line {line_number}")

        if section not in bindings_ledger:
            bindings_ledger[section] = {}

        section_ledger = bindings_ledger[section]
        section_ledger[key] = value

    return bindings_ledger
