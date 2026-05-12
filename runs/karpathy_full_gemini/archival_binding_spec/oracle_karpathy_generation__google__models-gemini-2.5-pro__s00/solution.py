import typing

def parse_bindings(lines: list[str]) -> typing.Dict[str, typing.Dict[str, str]]:
    """
    Parses a list of strings into a nested dictionary of bindings.

    Each line is expected to be in the format "section.key=value".
    Lines starting with '#' are comments and are ignored. Empty lines are
    also ignored. Whitespace around section, key, and value is stripped.

    Args:
        lines: A list of strings, where each string is a line from a
               configuration source.

    Returns:
        An insertion-ordered nested dictionary mapping section names to
        dictionaries of key-value pairs.

    Raises:
        ValueError: If a line is malformed, or if a section or key name
                    is empty after stripping whitespace.
    """
    sections_ledger: typing.Dict[str, typing.Dict[str, str]] = {}

    for line in lines:
        # Stage 1: Line preprocessing.
        # Ignore comments and empty lines.
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith('#'):
            continue

        # Stage 2: Parse the key-value pair.
        # The line must contain an '=' to separate the full key from the value.
        if '=' not in stripped_line:
            raise ValueError(
                "Malformed binding line: must contain an '=' separator."
            )
        full_key_part, value_part = stripped_line.split('=', 1)

        # Stage 3: Parse the section and key from the full key part.
        # The full key must contain a '.' to separate the section from the key.
        full_key = full_key_part.strip()
        if '.' not in full_key:
            raise ValueError(
                "Malformed binding key: must contain a '.' separator."
            )
        section_part, key_part = full_key.split('.', 1)

        # Stage 4: Finalize and validate components.
        # Strip whitespace from all parsed components and validate.
        section = section_part.strip()
        if not section:
            raise ValueError("Binding section name cannot be empty.")

        key = key_part.strip()
        if not key:
            raise ValueError("Binding key name cannot be empty.")

        value = value_part.strip()

        # Stage 5: Record the binding in the ledger.
        # This preserves the insertion order of sections and keys.
        if section not in sections_ledger:
            sections_ledger[section] = {}
        sections_ledger[section][key] = value

    return sections_ledger
