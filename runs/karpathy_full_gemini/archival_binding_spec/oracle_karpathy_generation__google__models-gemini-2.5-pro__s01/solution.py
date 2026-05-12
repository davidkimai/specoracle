"""
A module for parsing archival binding specifications.

This module provides a parser for a simple key-value configuration format
organized into sections, conforming to the Archival Binder Spec R-04.
"""

from typing import Dict, List


def parse_bindings(lines: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Parses a list of strings into a nested dictionary of bindings.

    Each non-empty, non-comment line must conform to the "section.key=value"
    format. Comments are lines that start with '#'. Whitespace around the
    section, key, and value is stripped.

    Args:
        lines: A list of strings, where each string is a line from the
               binding specification file.

    Returns:
        An insertion-ordered nested dictionary mapping section names to
        dictionaries of key-value pairs.

    Raises:
        ValueError: If a line is malformed, or if a section or key is empty.
    """
    sections_ledger: Dict[str, Dict[str, str]] = {}

    for line_number, line in enumerate(lines, 1):
        # Stage 1: Line preprocessing.
        # Ignore empty lines and comments.
        processed_line = line.strip()
        if not processed_line or processed_line.startswith('#'):
            continue

        # Stage 2: Structural parsing of the key-value assignment.
        # A valid line must contain an '=' separating the identifier from the value.
        if '=' not in processed_line:
            raise ValueError(
                f"Line {line_number}: Malformed binding, missing '=' separator."
            )
        identifier_part, value_part = processed_line.split('=', 1)

        # Stage 3: Structural parsing of the identifier.
        # The identifier must contain a '.' separating the section from the key.
        if '.' not in identifier_part:
            raise ValueError(
                f"Line {line_number}: Malformed binding, missing '.' in section.key part."
            )
        section_part, key_part = identifier_part.split('.', 1)

        # Stage 4: Value extraction and cleaning.
        # Strip whitespace from all components.
        section = section_part.strip()
        key = key_part.strip()
        value = value_part.strip()

        # Stage 5: Validation of semantic rules.
        # Section and key names must not be empty.
        if not section:
            raise ValueError(
                f"Line {line_number}: Archival field 'section' cannot be empty."
            )
        if not key:
            raise ValueError(
                f"Line {line_number}: Archival field 'key' cannot be empty."
            )

        # Stage 6: Ledger update.
        # Preserve insertion order for both sections and keys within sections.
        if section not in sections_ledger:
            sections_ledger[section] = {}

        sections_ledger[section][key] = value

    return sections_ledger
