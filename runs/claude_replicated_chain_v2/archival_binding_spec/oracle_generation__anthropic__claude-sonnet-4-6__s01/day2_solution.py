"""
Archival Binder Module R-04
Implements parse_bindings for structured section.key=value configuration lines.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse a list of configuration lines into a nested ordered dictionary.

    Each non-empty, non-comment line must follow the format:
        section.key=value

    Comments begin with '#'. Whitespace around section, key, and value is stripped.
    Input order is preserved in the returned dictionary.

    Raises ValueError for:
        - Lines that do not match the expected format
        - Empty section names
        - Empty key names
    """
    bindings_ledger: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        # Strip surrounding whitespace from the raw line
        stripped_line = raw_line.strip()

        # Skip empty lines
        if not stripped_line:
            continue

        # Skip comment lines
        if stripped_line.startswith("#"):
            continue

        # Stage 1: Split on '=' to separate the qualifier from the value
        if "=" not in stripped_line:
            raise ValueError(
                f"Archival field 'line' is malformed (missing '='): {stripped_line!r}"
            )

        equals_index = stripped_line.index("=")
        qualifier_part = stripped_line[:equals_index]
        value_part = stripped_line[equals_index + 1:]

        # Stage 2: Split the qualifier on '.' to separate section from key
        qualifier_stripped = qualifier_part.strip()
        if "." not in qualifier_stripped:
            raise ValueError(
                f"Archival field 'qualifier' is malformed (missing '.'): {qualifier_stripped!r}"
            )

        dot_index = qualifier_stripped.index(".")
        section_raw = qualifier_stripped[:dot_index]
        key_raw = qualifier_stripped[dot_index + 1:]

        # Stage 3: Strip whitespace from section, key, and value
        section = section_raw.strip()
        key = key_raw.strip()
        value = value_part.strip()

        # Stage 4: Validate that section and key are non-empty
        if not section:
            raise ValueError(
                f"Archival field 'section' must not be empty in line: {stripped_line!r}"
            )

        if not key:
            raise ValueError(
                f"Archival field 'key' must not be empty in line: {stripped_line!r}"
            )

        # Stage 5: Insert into the bindings ledger, preserving insertion order
        if section not in bindings_ledger:
            bindings_ledger[section] = {}

        bindings_ledger[section][key] = value

    return bindings_ledger


def flatten_bindings(bindings: dict[str, dict[str, str]]) -> list[str]:
    """
    Flatten a nested bindings dictionary into a list of "section.key=value" strings.

    Entries are emitted in dictionary iteration order (section order, then key
    order within each section).
    """
    result: list[str] = []
    for section, pairs in bindings.items():
        for key, value in pairs.items():
            result.append(f"{section}.{key}={value}")
    return result
