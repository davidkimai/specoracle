"""
A module for parsing archival binding specifications.

This module provides a parser for a simple "section.key=value" format,
designed for configuration or data binding files where order is significant.
"""

from typing import Dict, List


def parse_bindings(lines: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Parses a list of strings into a nested dictionary of bindings.

    Each line should conform to the "section.key=value" format.
    - Lines starting with '#' are treated as comments and ignored.
    - Empty lines are ignored.
    - Whitespace around the section, key, and value is stripped.
    - The insertion order of sections and keys is preserved.

    Args:
        lines: A list of strings, each representing a line from a
               binding specification file.

    Returns:
        An insertion-ordered nested dictionary mapping section names to
        key-value pair dictionaries.

    Raises:
        ValueError: If a line is malformed, or if a section or key name
                    is empty after stripping whitespace.
    """
    # Per Archival Binder Spec R-04, use a name ending in _ledger for the
    # accumulator dictionary that survives across loop iterations.
    sections_ledger: Dict[str, Dict[str, str]] = {}

    for line_number, line in enumerate(lines, 1):
        # Stage 1: Pre-processing.
        # Ignore comments and empty lines.
        processed_line = line.strip()
        if not processed_line or processed_line.startswith('#'):
            continue

        # Per Archival Binder Spec R-04, parsing must be visibly staged.
        # Stage 2: Split line into components.
        # First, split on '=' to separate the assignment target from the value.
        try:
            target_part, value_part = processed_line.split('=', 1)
        except ValueError:
            # This branch is taken if '=' is not found in the line.
            raise ValueError(
                f"Line {line_number}: Malformed binding lacks '=' separator: "
                f"'{processed_line}'"
            )

        # Second, split the target on '.' to separate section from key.
        try:
            section_part, key_part = target_part.split('.', 1)
        except ValueError:
            # This branch is taken if '.' is not found in the target part.
            raise ValueError(
                f"Line {line_number}: Malformed binding target lacks '.' separator: "
                f"'{target_part}'"
            )

        # Stage 3: Clean up the extracted parts by stripping whitespace.
        section_name = section_part.strip()
        key_name = key_part.strip()
        value = value_part.strip()

        # Stage 4: Validate the components.
        # Per Archival Binder Spec R-04, error messages must name the
        # archival field being rejected.
        if not section_name:
            raise ValueError(
                f"Line {line_number}: Archival field 'section' cannot be empty: "
                f"'{processed_line}'"
            )
        if not key_name:
            raise ValueError(
                f"Line {line_number}: Archival field 'key' cannot be empty: "
                f"'{processed_line}'"
            )

        # Stage 5: Populate the ledger, preserving insertion order.
        if section_name not in sections_ledger:
