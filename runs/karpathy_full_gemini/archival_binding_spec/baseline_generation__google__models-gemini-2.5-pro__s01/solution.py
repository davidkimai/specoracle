"""
A module for parsing key-value bindings from a list of strings.

This module provides a function to parse configuration lines in the format
"section.key=value" into a nested dictionary structure. It is designed to be
robust against common formatting issues like extra whitespace and handles
comments and empty lines gracefully.
"""

from typing import Dict, List

__all__ = ["parse_bindings"]


def parse_bindings(lines: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Parses a list of strings into a nested dictionary of bindings.

    Each non-empty, non-comment line must follow the "section.key=value" format.
    - Lines starting with '#' are treated as comments and ignored.
    - Empty lines (or lines containing only whitespace) are ignored.
    - Whitespace surrounding the section, key, and value is stripped.
    - The returned dictionary preserves the insertion order of sections and keys
      as they appear in the input.

    Args:
        lines: A list of strings, typically from a configuration file.

    Returns:
        An insertion-ordered nested dictionary mapping sections to key-value pairs.

    Raises:
        ValueError: If a line is malformed (e.g., does not contain '=', or the
                    key part does not contain '.'), or if a section or key name
                    is empty after stripping whitespace.
    """
    bindings: Dict[str, Dict[str, str]] = {}

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        if not line or line.startswith('#'):
            continue

        # Split the line into the full key part and the value part.
        # We split only on the first '=' to allow '=' characters in the value.
        parts = line.split('=', 1)
        if len(parts) != 2:
            raise ValueError(
                f"Line {line_num}: Malformed binding, expected 'section.key=value', "
                f"but found '{line}'"
            )

        full_key_str, value = parts
        full_key_str = full_key_str.strip()
        value = value.strip()

        # Split the full key into section and key.
        # We split only on the first '.' to allow '.' characters in the key,
        # although the spec doesn't require this, it's a robust choice.
        # The prompt implies a simple section.key structure, so splitting on
        # the first '.' is the most direct interpretation.
        key_parts = full_key_str.split('.', 1)
        if len(key_parts) != 2:
            raise ValueError(
                f"Line {line_num}: Malformed key, expected 'section.key', "
                f"but found '{full_key_str}'"
            )

        section, key = key_parts
        section = section.strip()
        key = key.strip()

        # Validate that section and key are not empty.
        if not section:
            raise ValueError(f"Line {line_num}: Section name cannot be empty in '{line}'")

        if not key:
            raise ValueError(f"Line {line_num}: Key name cannot be empty in '{line}'")

        # Populate the dictionary, creating the section if it's the first time.
        if section not in bindings:
            bindings[section] = {}

        bindings[section][key] = value

    return bindings
