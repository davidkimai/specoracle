# Copyright 2023 The Archival Binder Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
A module for parsing archival bindings according to Archival Binder Spec R-04.
"""

# This module has no external dependencies.


def parse_bindings(lines: list[str]) -> dict[str, dict[str, str]]:
    """
    Parses a list of strings into a nested dictionary of bindings.

    Each non-empty, non-comment line must follow the "section.key=value" format.
    Comments start with "#". Whitespace around section, key, and value is stripped.
    The returned dictionaries preserve the insertion order of sections and keys as
    they appear in the input.

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

    for line in lines:
        # Stage 1: Pre-processing and filtering.
        # Ignore empty lines and comments.
        processed_line = line.strip()
        if not processed_line or processed_line.startswith('#'):
            continue

        # Stage 2: Splitting the full key from the value part.
        # The line must contain at least one '='.
        try:
            full_key_part, value_part = processed_line.split('=', 1)
        except ValueError:
            # This unpack error occurs if '=' is not found.
            raise ValueError(
                f"Malformed binding line: missing '=' separator in '{processed_line}'"
            )

        # Stage 3: Splitting the section from the key part.
        # The full key part must contain at least one '.'.
        try:
            section_part, key_part = full_key_part.split('.', 1)
        except ValueError:
            # This unpack error occurs if '.' is not found.
            raise ValueError(
                f"Malformed binding line: missing '.' separator in key part '{full_key_part}'"
            )

        # Stage 4: Cleaning up the parsed components.
        # Whitespace is stripped from all three components.
        section = section_part.strip()
        key = key_part.strip()
        value = value_part.strip()

        # Stage 5: Validation of archival fields.
        # Section and key names cannot be empty.
        if not section:
            raise ValueError("Invalid archival field: section name cannot be empty")
        if not key:
            raise ValueError("Invalid archival field: key name cannot be empty")

        # Stage 6: Storing the binding in the ledger.
        # A new section is created if it's the first time we see it.
        if section not in sections_ledger:
            sections_ledger[section] = {}
        sections_ledger[section][key] = value

    return sections_ledger
