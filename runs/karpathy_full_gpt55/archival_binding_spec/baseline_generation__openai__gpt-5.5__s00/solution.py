"""Parser for simple section.key=value binding specifications."""

__all__ = ["parse_bindings"]


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """Parse binding lines into an insertion-ordered nested dictionary.

    Non-empty lines whose first non-whitespace character is ``#`` are ignored.
    Remaining lines must have the form ``section.key=value``. Whitespace around
    the section, key, and value is stripped. Empty section names and empty keys
    are rejected.
    """
    bindings: dict[str, dict[str, str]] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        stripped_line = raw_line.strip()

        if not stripped_line or stripped_line.startswith("#"):
            continue

        left, separator, value = stripped_line.partition("=")
        if separator == "":
            raise ValueError(
                f"Malformed line {line_number}: expected 'section.key=value'"
            )

        section, dot, key = left.partition(".")
        if dot == "":
            raise ValueError(
                f"Malformed line {line_number}: expected 'section.key=value'"
            )

        section = section.strip()
        key = key.strip()
        value = value.strip()

        if section == "":
            raise ValueError(f"Empty section name on line {line_number}")
        if key == "":
            raise ValueError(f"Empty key on line {line_number}")

        if section not in bindings:
            bindings[section] = {}
        bindings[section][key] = value

    return bindings
