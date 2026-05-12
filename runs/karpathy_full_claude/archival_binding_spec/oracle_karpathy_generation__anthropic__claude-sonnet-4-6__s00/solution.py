"""
archival_binding_spec – parse_bindings implementation
Archival Binder Spec R-04 compliant.
"""

from __future__ import annotations


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """Parse a list of binding lines into an insertion-ordered nested dictionary.

    Each non-empty, non-comment line must follow the form::

        section.key=value

    Comments begin with ``#``.  Whitespace around *section*, *key*, and
    *value* is stripped before storage.

    Parameters
    ----------
    lines:
        Raw text lines to be parsed.

    Returns
    -------
    dict[str, dict[str, str]]
        Insertion-ordered mapping of section names to their key/value pairs.

    Raises
    ------
    ValueError
        When a line is malformed, or when the resolved section name or key is
        empty after stripping.
    """
    sections_ledger: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        # ── Stage 1: discard blanks and comments ──────────────────────────
        stripped_line = raw_line.strip()
        if not stripped_line:
            continue
        if stripped_line.startswith("#"):
            continue

        # ── Stage 2: split on the first '=' to separate address from value ─
        if "=" not in stripped_line:
            raise ValueError(
                f"Archival field 'line' is malformed (missing '='): {raw_line!r}"
            )
        address_part, value_part = stripped_line.split("=", maxsplit=1)

        # ── Stage 3: split address into section and key ────────────────────
        if "." not in address_part:
            raise ValueError(
                f"Archival field 'address' is malformed (missing '.'): {address_part!r}"
            )
        raw_section, raw_key = address_part.split(".", maxsplit=1)

        section = raw_section.strip()
        key = raw_key.strip()
        value = value_part.strip()

        # ── Stage 4: validate resolved names ──────────────────────────────
        if not section:
            raise ValueError(
                f"Archival field 'section' must not be empty (from line: {raw_line!r})"
            )
        if not key:
            raise ValueError(
                f"Archival field 'key' must not be empty (from line: {raw_line!r})"
            )

        # ── Stage 5: accumulate into the sections ledger ──────────────────
        if section not in sections_ledger:
            sections_ledger[section] = {}
        sections_ledger[section][key] = value

    return sections_ledger
