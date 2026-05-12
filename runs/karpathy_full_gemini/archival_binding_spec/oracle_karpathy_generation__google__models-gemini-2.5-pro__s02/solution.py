"""
A module for parsing archival binding specifications.

This module provides a parser for a simple key-value configuration format
where keys are namespaced by a section, following the pattern
"section.key=value".
"""

# This module uses standard library features and requires no external imports.


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parses a list of strings into a nested dictionary of bindings.

    Each non-empty, non-comment line must conform to the "section.key=value"
    format. Comments are lines that start with "#". Whitespace around section,
    key, and value is stripped.

    The returned dictionary and its nested dictionaries preserve the insertion
    order of sections and keys as they appear in the input lines.

    Args:
        lines: A list of strings, where each string is a line from the
               binding configuration.

    Returns:
        An insertion-ordered nested dictionary mapping section names to
        dictionaries of key-value pairs.

    Raises:
        ValueError: If a line is malformed (e.g., missing '=' or '.'), or if
                    a section or key name is empty after stripping whitespace.
    """
    sections_ledger: dict[str, dict[str, str]] = {}

    for line_number, line in enumerate(lines, 1):
        # Stage 1: Line preprocessing.
        # Strip leading/trailing whitespace and ignore empty or comment lines.
        processed_line = line.strip()
        if not processed_line or processed_line.startswith('#'):
            continue

        # Stage 2: Split the line into the key specification and the value.
        # The split is done on the first equals sign to allow subsequent
        # equals signs in the value.
        binding_parts = processed_line.split('=', 1)
        if len(binding_parts) != 2:
            raise ValueError(
                f"Line {line_number}: Malformed binding, missing '=' separator. "
                f"Expected 'section.key=value', found '{processed_line}'."
            )
        
        key_spec, value = binding_parts
        key_spec = key_spec.strip()
        value = value.strip()

        # Stage 3: Split the key specification into section and key.
        # The split is done on the first dot to allow subsequent dots in the key.
        key_spec_parts = key_spec.split('.', 1)
        if len(key_spec_parts) != 2:
            raise ValueError(
                f"Line {line_number}: Malformed key specification, missing '.' separator. "
                f"Expected 'section.key', found '{key_spec}'."
            )
        
        section, key = key_spec_parts
        section = section.strip()
        key = key.strip()

        # Stage 4: Validate the parsed section and key names.
        if not section:
            raise ValueError(
                f"Line {line_number}: Rejected empty section name in key "
                f"specification '{key_spec}'."
            )
        if not key:
            raise ValueError(
                f"Line {line_number}: Rejected empty key in key "
                f"specification '{key_spec}'."
            )

        # Stage 5: Store the binding in the ledger.
        # A new section is created if it's the first time it's encountered.
        if section not in sections_ledger:
            sections_ledger[section] = {}
        
        sections_ledger[section][key] = value

    return sections_ledger
