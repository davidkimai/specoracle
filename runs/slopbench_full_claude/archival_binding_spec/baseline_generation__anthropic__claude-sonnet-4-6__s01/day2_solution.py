"""
archival_binding_spec module
Provides parse_bindings for parsing section.key=value configuration lines,
and flatten_bindings for serialising the nested dictionary back to lines.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parse a list of strings in "section.key=value" format.

    Parameters
    ----------
    lines : list[str]
        Input lines to parse.

    Returns
    -------
    dict[str, dict[str, str]]
        Insertion-ordered nested dictionary mapping section names to
        key/value pairs.

    Raises
    ------
    ValueError
        If a line is malformed, has an empty section name, or has an empty key.
    """
    result: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        # Strip surrounding whitespace from the whole line
        line = raw_line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Must contain '=' to be valid
        if "=" not in line:
            raise ValueError(
                f"Malformed line (missing '='): {raw_line!r}"
            )

        # Split on the first '=' only
        lhs, value = line.split("=", 1)
        value = value.strip()

        # lhs must contain '.' to separate section from key
        if "." not in lhs:
            raise ValueError(
                f"Malformed line (missing '.' in section.key): {raw_line!r}"
            )

        # Split on the first '.' only so keys may contain dots if needed
        section, key = lhs.split(".", 1)
        section = section.strip()
        key = key.strip()

        if not section:
            raise ValueError(
                f"Empty section name in line: {raw_line!r}"
            )

        if not key:
            raise ValueError(
                f"Empty key in line: {raw_line!r}"
            )

        if section not in result:
            result[section] = {}

        result[section][key] = value

    return result


def flatten_bindings(bindings: dict[str, dict[str, str]]) -> list[str]:
    """
    Serialise a nested section/key/value dictionary back to a list of strings.

    Parameters
    ----------
    bindings : dict[str, dict[str, str]]
        Nested dictionary as returned by parse_bindings.

    Returns
    -------
    list[str]
        Lines in "section.key=value" format, in dictionary iteration order.
    """
    result: list[str] = []
    for section, pairs in bindings.items():
        for key, value in pairs.items():
            result.append(f"{section}.{key}={value}")
    return result
