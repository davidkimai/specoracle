"""
Archival Binder Module (Spec R-04)
Provides parse_bindings for structured section.key=value input.
"""


def _split_on_equals(raw_line: str) -> tuple[str, str]:
    """Stage 2: split a stripped line on '=' into qualifier and value parts."""
    stripped_line = raw_line.strip()
    if "=" not in stripped_line:
        raise ValueError(
            f"Archival field 'line' is malformed (missing '='): {raw_line!r}"
        )
    qualifier_part, _, value_part = stripped_line.partition("=")
    return qualifier_part.strip(), value_part.strip()


def _split_qualifier(qualifier: str, raw_line: str) -> tuple[str, str]:
    """Stage 3: split the qualifier on '.' into section and key."""
    if "." not in qualifier:
        raise ValueError(
            f"Archival field 'qualifier' is malformed (missing '.'): {qualifier!r}"
        )
    dot_index = qualifier.index(".")
    section = qualifier[:dot_index].strip()
    key = qualifier[dot_index + 1:].strip()
    return section, key


def _validate_section_and_key(section: str, key: str, raw_line: str) -> None:
    """Stage 4: validate that section and key are non-empty."""
    if not section:
        raise ValueError(
            f"Archival field 'section' must not be empty in line: {raw_line!r}"
        )
    if not key:
        raise ValueError(
            f"Archival field 'key' must not be empty in line: {raw_line!r}"
        )


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """Parse lines of the form 'section.key=value' into a nested dict.

    Comments (lines starting with '#') and blank lines are skipped.
    Whitespace around section, key, and value is stripped.
    Returns an insertion-ordered nested dictionary mapping sections to
    their key/value pairs.

    Raises ValueError for malformed lines, empty section names, or empty keys.
    """
    sections_ledger: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        # Stage 1: skip blank lines and comments
        stripped_line = raw_line.strip()
        if not stripped_line or stripped_line.startswith("#"):
            continue

        # Stage 2: split on '=' to separate qualifier from value
        qualifier, value = _split_on_equals(raw_line)

        # Stage 3: split qualifier on '.' to separate section from key
        section, key = _split_qualifier(qualifier, raw_line)

        # Stage 4: validate section and key are non-empty
        _validate_section_and_key(section, key, raw_line)

        # Stage 5: insert into the sections ledger, preserving insertion order
        if section not in sections_ledger:
            sections_ledger[section] = {}
        sections_ledger[section][key] = value

    return sections_ledger
