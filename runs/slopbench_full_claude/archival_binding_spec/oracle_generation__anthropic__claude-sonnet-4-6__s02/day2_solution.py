"""
Archival Binder Module (Spec R-04)
Parses structured binding lines into a nested, insertion-ordered dictionary.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse a list of strings into a nested dictionary of sections to key/value pairs.

    Each non-empty, non-comment line must follow the format: section.key=value
    Comments begin with '#'. Whitespace around section, key, and value is stripped.
    Input order is preserved in the returned dictionary.

    Raises ValueError for:
    - Lines that do not conform to 'section.key=value' format
    - Empty section names
    - Empty key names
    """
    bindings_ledger: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        # Stage 1: Strip outer whitespace and skip blank lines and comments
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Stage 2: Split on '=' to isolate the section.key portion from the value
        if "=" not in line:
            raise ValueError(
                f"Archival field 'line' is malformed (missing '='): {raw_line!r}"
            )
        eq_index = line.index("=")
        section_key_part = line[:eq_index]
        value = line[eq_index + 1:].strip()

        # Stage 3: Split section.key part on '.' to isolate section and key
        if "." not in section_key_part:
            raise ValueError(
                f"Archival field 'section.key' is malformed (missing '.'): {raw_line!r}"
            )
        dot_index = section_key_part.index(".")
        section = section_key_part[:dot_index].strip()
        key = section_key_part[dot_index + 1:].strip()

        # Stage 4: Validate that section and key are non-empty
        if not section:
            raise ValueError(
                f"Archival field 'section' is empty in line: {raw_line!r}"
            )
        if not key:
            raise ValueError(
                f"Archival field 'key' is empty in line: {raw_line!r}"
            )

        # Stage 5: Insert into the bindings ledger, preserving insertion order
        if section not in bindings_ledger:
            bindings_ledger[section] = {}
        bindings_ledger[section][key] = value

    return bindings_ledger


def flatten_bindings(bindings: dict[str, dict[str, str]]) -> list[str]:
    """
    Flatten a nested bindings dictionary into a list of 'section.key=value' strings.

    Returns entries in dictionary iteration order (section order, then key order
    within each section).
    """
    result: list[str] = []
    for section, pairs in bindings.items():
        for key, value in pairs.items():
            result.append(f"{section}.{key}={value}")
    return result
