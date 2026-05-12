"""
A module for parsing archival binding specifications.
"""

from __future__ import annotations

__all__ = ["parse_bindings"]


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parses a list of configuration lines into a nested dictionary.

    The format for each significant line is "section.key=value".

    Rules:
    - Lines starting with '#' are treated as comments and are ignored.
    - Empty lines, after stripping whitespace, are also ignored.
    - Whitespace surrounding the section, key, and value components is stripped.
    - The returned dictionary and its nested dictionaries preserve the insertion
      order based on the first appearance of a section or key. Standard Python
      dictionaries (3.7+) are used to maintain this order.

    Args:
        lines: A list of strings, where each string represents a line of
               the configuration to be parsed.

    Returns:
        An insertion-ordered nested dictionary mapping section names to
        dictionaries of key-value pairs.

    Raises:
        ValueError: If any line is malformed. This includes lines that do
                    not conform to the "section.key=value" structure, or
                    lines where the section or key is empty after stripping
                    whitespace.
    """
    bindings: dict[str, dict[str, str]] = {}

    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()

        if not stripped_line or stripped_line.startswith('#'):
            continue

        # Each line must contain exactly one '=' to separate the key-spec from the value.
        parts = stripped_line.split('=', 1)
        if len(parts) != 2:
            raise ValueError(
                f"Line {line_num}: Malformed binding, expected 'section.key=value', "
                f"but found no '=' separator: '{line}'"
            )
        full_key_spec, value_str = parts

        # The key-spec must contain exactly one '.' to separate section from key.
        key_parts = full_key_spec.split('.', 1)
        if len(key_parts) != 2:
            raise ValueError(
                f"Line {line_num}: Malformed key specification, expected 'section.key', "
                f"but found no '.' separator: '{full_key_spec}'"
            )
        section_str, key_str = key_parts

        section = section_str.strip()
        key = key_str.strip()
        value = value_str.strip()

        # Section and key names cannot be empty.
        if not section:
            raise ValueError(
                f"Line {line_num}: Section name cannot be empty: '{line}'"
            )
        if not key:
            raise ValueError(
                f"Line {line_num}: Key name cannot be empty: '{line}'"
            )

        # Populate the bindings dictionary, creating a new section if necessary.
        if section not in bindings:
            bindings[section] = {}
        bindings[section][key] = value

    return bindings
