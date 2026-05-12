"""
Archival Binder Module R-04
Provides parse_bindings for structured section.key=value input parsing.
"""


def _is_ignorable(stripped_line: str) -> bool:
    """Return True if the line should be skipped (blank or comment)."""
    if not stripped_line:
        return True
    if stripped_line.startswith("#"):
        return True
    return False


def _split_on_equals(stripped_line: str, raw_line: str) -> tuple[str, str]:
    """Split a stripped line into (dotted_key_raw, value_raw) on the first '='."""
    if "=" not in stripped_line:
        raise ValueError(
            f"Archival field 'line' is malformed (missing '='): {raw_line!r}"
        )
    equals_index = stripped_line.index("=")
    dotted_key_raw = stripped_line[:equals_index]
    value_raw = stripped_line[equals_index + 1:]
    return dotted_key_raw, value_raw


def _split_dotted_key(dotted_key: str, raw_line: str) -> tuple[str, str]:
    """Split a dotted key string into (section, key), validating both are non-empty."""
    if "." not in dotted_key:
        raise ValueError(
            f"Archival field 'line' is malformed (missing '.' separator): {raw_line!r}"
        )
    dot_index = dotted_key.index(".")
    section = dotted_key[:dot_index].strip()
    key = dotted_key[dot_index + 1:].strip()

    if not section:
        raise ValueError(
            f"Archival field 'section' is empty in line: {raw_line!r}"
        )
    if not key:
        raise ValueError(
            f"Archival field 'key' is empty in line: {raw_line!r}"
        )
    return section, key


def _parse_single_line(raw_line: str) -> tuple[str, str, str] | None:
    """
    Parse one raw line into (section, key, value).
    Returns None if the line should be ignored.
    """
    stripped_line = raw_line.strip()

    if _is_ignorable(stripped_line):
        return None

    dotted_key_raw, value_raw = _split_on_equals(stripped_line, raw_line)

    dotted_key = dotted_key_raw.strip()
    value = value_raw.strip()

    section, key = _split_dotted_key(dotted_key, raw_line)

    return section, key, value


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse a list of strings in 'section.key=value' format into a nested dict.

    Rules:
    - Empty lines and lines starting with '#' are skipped.
    - Each valid line must match the pattern: section.key=value
    - Whitespace around section, key, and value is stripped.
    - Sections and keys must be non-empty after stripping.
    - Returns an insertion-ordered nested dictionary.
    - Raises ValueError with a descriptive message for any malformed input.
    """
    sections_ledger: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        result = _parse_single_line(raw_line)

        if result is None:
            continue

        section, key, value = result

        if section not in sections_ledger:
            sections_ledger[section] = {}
        sections_ledger[section][key] = value

    return sections_ledger
