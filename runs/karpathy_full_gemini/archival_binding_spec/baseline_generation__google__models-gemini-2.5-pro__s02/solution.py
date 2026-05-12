"""
A module for parsing archival binding specifications.
"""

from __future__ import annotations

__all__ = ["parse_bindings"]


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parses configuration lines into a nested, insertion-ordered dictionary.

    Each non-empty, non-comment line must be in the format "section.key=value".
    Lines starting with '#' are treated as comments and are ignored.
    Empty lines are also ignored. Whitespace around the section, key, and
    value is stripped before processing.

    Args:
        lines: A list of strings, where each string is a line of
               configuration data.

    Returns:
        An insertion-ordered nested dictionary mapping section names to
        dictionaries of key-value pairs. The insertion order reflects the
        first appearance of each section and key in the input.

    Raises:
        ValueError: If a line is malformed (e.g., missing '=', missing '.',
                    an empty section name, or an empty key name).
    """
    bindings: dict[str, dict[str, str]] = {}

    for line_num, line in enumerate(lines, 1):
        # 1. Pre-process the line
        line = line.strip()

        # Ignore empty lines and comments
        if not line or line.startswith('#'):
            continue

        # 2. Parse the "key=value" structure
        parts = line.split('=', 1)
        if len(parts) != 2:
            raise ValueError(
                f"Line {line_num}: Malformed entry, missing '=' separator: '{line}'"
            )

        full_key, value = parts
        value = value.strip()

        # 3. Parse the "section.key" structure
        full_key = full_key.strip()
        key_parts = full_key.split('.', 1)
        if len(key_parts) != 2:
            raise ValueError(
                f"Line {line_num}: Malformed key, missing '.' separator: '{full_key}'"
            )

        section, key = key_parts
        section = section.strip()
        key = key.strip()

        # 4. Validate section and key names
        if not section:
            raise ValueError(
                f"Line {line_num}: Section name cannot be empty: '{line}'"
            )
        if not key:
            raise ValueError(
                f"Line {line_num}: Key name cannot be empty: '{line}'"
            )

        # 5. Populate the nested dictionary
        if section not in bindings:
            bindings[section] = {}
        bindings[section][key] = value

    return bindings
