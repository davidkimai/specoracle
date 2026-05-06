"""
archival_binding_spec – parse_bindings implementation
Archival Binder Spec R-04 compliant.
"""


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """Parse a list of binding lines into an insertion-ordered nested dict.

    Each non-empty, non-comment line must follow the form::

        section.key = value

    Comments begin with ``#``. Whitespace around *section*, *key*, and
    *value* is stripped.  Returns a nested dictionary mapping each section
    name to an insertion-ordered dictionary of key/value pairs.

    Raises
    ------
    ValueError
        For malformed lines, empty section names, or empty keys.
    """
    bindings_ledger: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        # ── Stage 1: discard blanks and comments ──────────────────────────
        stripped_line = raw_line.strip()
        if not stripped_line:
            continue
        if stripped_line.startswith("#"):
            continue

        # ── Stage 2: split on the first '=' to separate lhs from value ───
        if "=" not in stripped_line:
            raise ValueError(
                f"Archival field 'line' is malformed (missing '='): {raw_line!r}"
            )
        lhs, _, raw_value = stripped_line.partition("=")
        value = raw_value.strip()

        # ── Stage 3: split lhs on the first '.' to separate section/key ──
        lhs_stripped = lhs.strip()
        if "." not in lhs_stripped:
            raise ValueError(
                f"Archival field 'line' is malformed (missing '.' in key path): {raw_line!r}"
            )
        raw_section, _, raw_key = lhs_stripped.partition(".")
        section = raw_section.strip()
        key = raw_key.strip()

        # ── Stage 4: validate section and key are non-empty ───────────────
        if not section:
            raise ValueError(
                f"Archival field 'section' is empty in line: {raw_line!r}"
            )
        if not key:
            raise ValueError(
                f"Archival field 'key' is empty in line: {raw_line!r}"
            )

        # ── Stage 5: record into the bindings ledger ──────────────────────
        if section not in bindings_ledger:
            bindings_ledger[section] = {}
        bindings_ledger[section][key] = value

    return bindings_ledger


def flatten_bindings(bindings: dict[str, dict[str, str]]) -> list[str]:
    """Flatten a nested bindings dict back into a list of binding lines.

    Returns a list of strings in the form ``"section.key=value"`` following
    the dictionary iteration order of both the outer and inner mappings.

    Parameters
    ----------
    bindings:
        A nested dictionary as returned by :func:`parse_bindings`.

    Returns
    -------
    list[str]
        One entry per key/value pair across all sections.
    """
    result: list[str] = []
    for section, pairs in bindings.items():
        for key, value in pairs.items():
            result.append(f"{section}.{key}={value}")
    return result
