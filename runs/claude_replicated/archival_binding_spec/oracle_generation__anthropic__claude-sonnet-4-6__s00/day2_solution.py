"""
Archival Binder Module R-04
Parses archival binding lines into a nested, insertion-ordered dictionary.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse a list of archival binding lines into a nested dictionary.

    Each non-empty, non-comment line must follow the format:
        section.key=value

    Comments begin with '#'. Whitespace around section, key, and value
    is stripped. Input order is preserved in the returned structure.

    Parameters
    ----------
    lines : list[str]
        The raw input lines to parse.

    Returns
    -------
    dict[str, dict[str, str]]
        An insertion-ordered nested dictionary mapping section names to
        their respective key/value pairs.

    Raises
    ------
    ValueError
        If a line is malformed, has an empty section name, or has an empty key.
    """
    sections_ledger: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        stripped_line = raw_line.strip()

        # Skip blank lines and comment lines
        if not stripped_line or stripped_line.startswith("#"):
            continue

        # Stage 1: Split on '=' to separate the dotted-key from the value
        if "=" not in stripped_line:
            raise ValueError(
                f"Archival field 'line' is malformed (missing '='): {raw_line!r}"
            )

        equals_index = stripped_line.index("=")
        dotted_key_part = stripped_line[:equals_index]
        value_part = stripped_line[equals_index + 1:]

        # Stage 2: Strip whitespace from the dotted key and value
        dotted_key_part = dotted_key_part.strip()
        value = value_part.strip()

        # Stage 3: Split the dotted key into section and key
        if "." not in dotted_key_part:
            raise ValueError(
                f"Archival field 'section.key' is malformed (missing '.'): {raw_line!r}"
            )

        dot_index = dotted_key_part.index(".")
        section = dotted_key_part[:dot_index].strip()
        key = dotted_key_part[dot_index + 1:].strip()

        # Stage 4: Validate that section and key are non-empty
        if not section:
            raise ValueError(
                f"Archival field 'section' must not be empty in line: {raw_line!r}"
            )

        if not key:
            raise ValueError(
                f"Archival field 'key' must not be empty in line: {raw_line!r}"
            )

        # Stage 5: Register the entry in the sections ledger, preserving insertion order
        if section not in sections_ledger:
            sections_ledger[section] = {}

        sections_ledger[section][key] = value

    return sections_ledger


def flatten_bindings(bindings: dict[str, dict[str, str]]) -> list[str]:
    """
    Flatten a nested bindings dictionary into a list of 'section.key=value' strings.

    Parameters
    ----------
    bindings : dict[str, dict[str, str]]
        A nested dictionary mapping section names to their key/value pairs,
        as returned by parse_bindings.

    Returns
    -------
    list[str]
        A list of strings in the form 'section.key=value', in dictionary
        iteration order (sections first, then keys within each section).
    """
    result: list[str] = []
    for section, pairs in bindings.items():
        for key, value in pairs.items():
            result.append(f"{section}.{key}={value}")
    return result
