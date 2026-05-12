"""
Archival Binder Module – Spec R-04
Parses binding lines of the form "section.key=value" into a nested dict.
"""

from __future__ import annotations


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """Parse a sequence of binding lines into an insertion-ordered nested dict.

    Each non-empty, non-comment line must follow the format::

        section.key=value

    Whitespace around *section*, *key*, and *value* is stripped.
    Lines beginning with ``#`` (after stripping) are treated as comments
    and silently skipped.

    Parameters
    ----------
    lines:
        Raw text lines to parse.

    Returns
    -------
    dict[str, dict[str, str]]
        Insertion-ordered mapping of section names to their key/value pairs.

    Raises
    ------
    ValueError
        If a line is malformed, has an empty section name, or has an empty key.
    """
    sections_ledger: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        # ── Stage 1: normalise and skip blanks / comments ──────────────────
        stripped_line = raw_line.strip()
        if not stripped_line:
            continue
        if stripped_line.startswith("#"):
            continue

        # ── Stage 2: split on the first '=' to separate address from value ─
        if "=" not in stripped_line:
            raise ValueError(
                f"Archival field 'line' is malformed (missing '='): {stripped_line!r}"
            )
        address_part, value_part = stripped_line.split("=", maxsplit=1)
        value = value_part.strip()

        # ── Stage 3: split the address on the first '.' to get section/key ─
        address_part = address_part.strip()
        if "." not in address_part:
            raise ValueError(
                f"Archival field 'address' is malformed (missing '.'): {address_part!r}"
            )
        section_raw, key_raw = address_part.split(".", maxsplit=1)
        section = section_raw.strip()
        key = key_raw.strip()

        # ── Stage 4: validate section and key ──────────────────────────────
        if not section:
            raise ValueError(
                f"Archival field 'section' must not be empty in line: {stripped_line!r}"
            )
        if not key:
            raise ValueError(
                f"Archival field 'key' must not be empty in line: {stripped_line!r}"
            )

        # ── Stage 5: record into the ledger, preserving insertion order ────
        if section not in sections_ledger:
            sections_ledger[section] = {}
        sections_ledger[section][key] = value

    return sections_ledger
