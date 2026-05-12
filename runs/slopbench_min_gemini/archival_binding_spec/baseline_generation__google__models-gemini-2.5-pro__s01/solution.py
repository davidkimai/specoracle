# -*- coding: utf-8 -*-
"""
A module for parsing archival binding specifications.
"""

import typing

__all__ = ["parse_bindings"]


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parses a list of strings into a nested dictionary of bindings.

    Each non-empty, non-comment line must be in the format "section.key=value".
    Comments start with "#". Whitespace around the section, key, and value
    is stripped before processing. The returned dictionary preserves the
    insertion order of sections and keys as they appear in the input.

    Args:
        lines: A list of strings, typically from a configuration file.

    Returns:
        An insertion-ordered nested dictionary mapping section names to
        key-value pairs. For example:
        {
            "section1": {"key1": "value1", "key2": "value2"},
            "section2": {"key3": "value3"}
        }

    Raises:
        ValueError: If a line is malformed (e.g., missing '=', missing '.'),
                    or if a section or key name is empty after stripping
                    whitespace.
    """
    bindings: dict[str, dict[str, str]] = {}

    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()

        # Ignore empty lines and comments
        if not stripped_line or stripped_line.startswith('#'):
            continue

        # Each line must contain exactly one '=' separator.
        # We split only on the first occurrence to allow '=' in the value.
        parts = stripped_line.split('=', 1)
        if len(parts) != 2:
            raise ValueError(
                f"Line {line_num}: Malformed binding, missing '=' separator: "
                f"'{stripped_line}'"
            )

        full_key_str, value_str = parts
        value = value_str.strip()

        # The part before '=' must contain exactly one '.' separator.
        key_parts = full_key_str.split('.', 1)
        if len(key_parts) != 2:
            raise ValueError(
                f"Line {line_num}: Malformed key, missing '.' separator in "
                f"'{full_key_str.strip()}'"
            )

        section_str, key_str = key_parts
        section = section_str.strip()
        key = key_str.strip()

        # Section and key names cannot be empty.
        if not section:
            raise ValueError(
                f"Line {line_num}: Section name cannot be empty: '{stripped_line}'"
            )
        if not key:
            raise ValueError(
                f"Line {line_num}: Key name cannot be empty: '{stripped_line}'"
            )

        # Add the parsed key-value pair to the corresponding section.
        if section not in bindings:
            bindings[section] = {}
        bindings[section][key] = value

    return bindings
