"""
Archival Binder Module — Spec R-04
Provides parse_bindings for structured section.key=value input.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse a list of text lines into a nested ordered dictionary.

    Each meaningful line must follow the pattern:
        section.key=value

    Lines that are empty or begin with '#' (after stripping) are skipped.
    Whitespace around section, key, and value is stripped.

    Returns:
        A dict mapping section names to dicts of key/value pairs,
        preserving insertion order throughout.

    Raises:
        ValueError: For malformed lines, empty section names, or empty keys.
    """
    sections_ledger: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        # Stage 1: Normalise the raw line.
        stripped_line = raw_line.strip()

        # Stage 2: Skip blank lines and comments.
        if not stripped_line:
            continue
        if stripped_line.startswith("#"):
            continue

        # Stage 3: Split on the first '=' to separate the address from the value.
        if "=" not in stripped_line:
            raise ValueError(
                f"Archival field 'line' is malformed (missing '='): {raw_line!r}"
            )
        address_part, value_part = stripped_line.split("=", 1)
        value = value_part.strip()

        # Stage 4: Split the address on the first '.' to separate section from key.
        address_part = address_part.strip()
        if "." not in address_part:
            raise ValueError(
                f"Archival field 'address' is malformed (missing '.'): {address_part!r}"
            )
        section_raw, key_raw = address_part.split(".", 1)

        # Stage 5: Validate section and key after stripping.
        section = section_raw.strip()
        key = key_raw.strip()

        if not section:
            raise ValueError(
                f"Archival field 'section' must not be empty in line: {raw_line!r}"
            )
        if not key:
            raise ValueError(
                f"Archival field 'key' must not be empty in line: {raw_line!r}"
            )

        # Stage 6: Insert into the ledger, preserving insertion order.
        if section not in sections_ledger:
            sections_ledger[section] = {}

        keys_ledger = sections_ledger[section]
        keys_ledger[key] = value

    return sections_ledger
