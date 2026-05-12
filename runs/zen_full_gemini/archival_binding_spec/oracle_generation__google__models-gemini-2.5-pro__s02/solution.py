import typing

def parse_bindings(
    lines: typing.List[str],
) -> typing.Dict[str, typing.Dict[str, str]]:
    """
    Parses a list of strings into a nested dictionary of bindings.

    Each non-empty, non-comment line must conform to the "section.key=value"
    format. Comments start with "#". Whitespace around section, key, and
    value is stripped.

    Args:
        lines: A list of strings, typically from a configuration file.

    Returns:
        An insertion-ordered nested dictionary mapping section names to
        dictionaries of key-value pairs.

    Raises:
        ValueError: If a line is malformed, or if a section or key is empty.
    """
    sections_ledger: typing.Dict[str, typing.Dict[str, str]] = {}

    for line_number, line in enumerate(lines, 1):
        # Stage 1: Line pre-processing
        # Ignore empty lines and comments.
        processed_line = line.strip()
        if not processed_line or processed_line.startswith('#'):
            continue

        # Stage 2: Parse assignment from "section.key=value"
        # The line must contain exactly one '=' separator.
        assignment_parts = processed_line.split('=', 1)
        if len(assignment_parts) != 2:
            raise ValueError(
                f"Line {line_number}: Malformed line. "
                f"Expected 'section.key=value' format."
            )
        full_key_part, value_part = assignment_parts

        # Stage 3: Parse qualified key from "section.key"
        # The part before '=' must contain exactly one '.' separator.
        qualified_key = full_key_part.strip()
        qualifier_parts = qualified_key.split('.', 1)
        if len(qualifier_parts) != 2:
            raise ValueError(
                f"Line {line_number}: Invalid key '{qualified_key}'. "
                f"Must be in 'section.key' format."
            )
        section_part, key_part = qualifier_parts

        # Stage 4: Strip and validate components
        section = section_part.strip()
        if not section:
            raise ValueError(
                f"Line {line_number}: Archival field 'section' cannot be empty."
            )

        key = key_part.strip()
        if not key:
            raise ValueError(
                f"Line {line_number}: Archival field 'key' cannot be empty."
            )

        value = value_part.strip()

        # Stage 5: Populate ledger, preserving insertion order
        if section not in sections_ledger:
            sections_ledger[section] = {}
        sections_ledger[section][key] = value

    return sections_ledger
