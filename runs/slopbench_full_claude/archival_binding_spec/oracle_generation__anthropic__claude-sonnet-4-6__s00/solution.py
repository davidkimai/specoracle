"""
Archival Binder Module — Spec R-04
Parses binding lines of the form "section.key=value" into a nested dict.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse a list of binding lines into an insertion-ordered nested dictionary.

    Each non-empty, non-comment line must follow the format:
        section.key=value

    Comments begin with '#'. Whitespace around section, key, and value is
    stripped. Returns a dict mapping section names to dicts of key/value pairs.

    Raises ValueError for malformed lines, empty section names, or empty keys.
    """
    bindings_ledger: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        # Stage 1: Strip the raw line and skip blanks and comments.
        stripped_line = raw_line.strip()
        if not stripped_line:
            continue
        if stripped_line.startswith("#"):
            continue

        # Stage 2: Split on the first '=' to separate the address from the value.
        if "=" not in stripped_line:
            raise ValueError(
                f"Archival field 'line' is malformed (missing '='): {stripped_line!r}"
            )
        address_part, _, value_part = stripped_line.partition("=")

        # Stage 3: Strip whitespace from address and value.
        address_part = address_part.strip()
        value_part = value_part.strip()

        # Stage 4: Split the address on the first '.' to separate section from key.
        if "." not in address_part:
            raise ValueError(
                f"Archival field 'address' is malformed (missing '.'): {address_part!r}"
            )
        section_part, _, key_part = address_part.partition(".")

        # Stage 5: Strip whitespace from section and key.
        section_part = section_part.strip()
        key_part = key_part.strip()

        # Stage 6: Validate that section and key are non-empty.
        if not section_part:
            raise ValueError(
                f"Archival field 'section' must not be empty in line: {stripped_line!r}"
            )
        if not key_part:
            raise ValueError(
                f"Archival field 'key' must not be empty in line: {stripped_line!r}"
            )

        # Stage 7: Insert into the bindings ledger, preserving insertion order.
        if section_part not in bindings_ledger:
            bindings_ledger[section_part] = {}
        bindings_ledger[section_part][key_part] = value_part

    return bindings_ledger
