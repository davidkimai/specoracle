"""
A module for parsing archival bindings from a list of strings.

This module provides a parser for a simple key-value configuration format
where keys are structured as 'section.key'.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parses a list of strings into a nested dictionary of bindings.

    Each non-empty, non-comment line must be "section.key=value". Comments
    start with "#". Whitespace around section, key, and value is stripped.

    The returned dictionary and its nested dictionaries preserve the insertion
    order of sections and keys as they appear in the input lines.

    Args:
        lines: A list of strings, each representing a line from a configuration
               source.

    Returns:
        An insertion-ordered nested dictionary mapping section names to
        key-value pair dictionaries.

    Raises:
        ValueError: If a line is malformed (e.g., missing '=' or '.'), or if
                    a section or key name is empty after stripping whitespace.
    """
    sections_ledger: dict[str, dict[str, str]] = {}

    for line in lines:
        # Stage 1: Pre-processing and filtering.
        # This step cleans up the line and skips comments or empty lines.
        processed_line = line.strip()
        if not processed_line or processed_line.startswith('#'):
            continue

        # Stage 2: Splitting value from the key specification.
        # A binding must contain an '=' to separate the key spec from the value.
        if '=' not in processed_line:
            raise ValueError(
                f"Malformed binding: missing '=' separator in line: '{line}'"
            )
        key_spec_part, value_part = processed_line.split('=', 1)

        # Stage 3: Splitting section from the key.
        # The key specification must contain a '.' to separate the section
        # from the key name.
        if '.' not in key_spec_part:
            raise ValueError(
                "Malformed binding: missing '.' separator in key specification "
                f"'{key_spec_part}'"
            )
        section_part, key_part = key_spec_part.split('.', 1)

        # Stage 4: Cleaning the parsed components.
        # This ensures that surrounding whitespace doesn't affect names or values.
        section_name = section_part.strip()
        key_name = key_part.strip()
        value = value_part.strip()

        # Stage 5: Validation of required identifier fields.
        # Archival sections and keys must have non-empty names.
        if not section_name:
            raise ValueError("Archival field rejected: section name cannot be empty")
        if not key_name:
            raise ValueError("Archival field rejected: key cannot be empty")

        # Stage 6: Populating the ledger.
        # The parsed and validated data is stored in the result dictionary.
        # A new inner dictionary is created for the first key in a section.
        if section_name not in sections_ledger:
            sections_ledger[section_name] = {}
        sections_ledger[section_name][key_name] = value

    return sections_ledger
