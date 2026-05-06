"""
Archival Binder Module — Spec R-04
Implements parse_bindings for structured section.key=value input.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """Parse a list of strings into a nested section -> key -> value mapping.

    Each non-empty, non-comment line must follow the format:
        section.key=value

    Comments begin with '#'. Whitespace around section, key, and value is
    stripped. Input order is preserved in the returned dictionaries.

    Raises ValueError for malformed lines, empty section names, or empty keys.
    """
    sections_ledger: dict[str, dict[str, str]] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        # Stage 1: Strip surrounding whitespace and skip blank lines or comments.
        stripped_line = raw_line.strip()
        if not stripped_line:
            continue
        if stripped_line.startswith("#"):
            continue

        # Stage 2: Split on the first '=' to separate the address from the value.
        if "=" not in stripped_line:
            raise ValueError(
                f"Line {line_number}: malformed archival field — "
                f"missing '=' separator in {stripped_line!r}"
            )
        address_part, _, value_part = stripped_line.partition("=")
        value = value_part.strip()

        # Stage 3: Split the address on the first '.' to separate section from key.
        address = address_part.strip()
        if "." not in address:
            raise ValueError(
                f"Line {line_number}: malformed archival field — "
                f"missing '.' separator in address {address!r}"
            )
        section_raw, _, key_raw = address.partition(".")
        section = section_raw.strip()
        key = key_raw.strip()

        # Stage 4: Validate that section and key are non-empty.
        if not section:
            raise ValueError(
                f"Line {line_number}: archival field 'section' is empty "
                f"in line {stripped_line!r}"
            )
        if not key:
            raise ValueError(
                f"Line {line_number}: archival field 'key' is empty "
                f"in line {stripped_line!r}"
            )

        # Stage 5: Insert into the sections ledger, preserving insertion order.
        if section not in sections_ledger:
            sections_ledger[section] = {}
        sections_ledger[section][key] = value

    return sections_ledger


def flatten_bindings(bindings: dict[str, dict[str, str]]) -> list[str]:
    """Flatten a nested section -> key -> value mapping into a list of strings.

    Returns entries in dictionary iteration order as "section.key=value".
    """
    result: list[str] = []
    for section, keys in bindings.items():
        for key, value in keys.items():
            result.append(f"{section}.{key}={value}")
    return result
