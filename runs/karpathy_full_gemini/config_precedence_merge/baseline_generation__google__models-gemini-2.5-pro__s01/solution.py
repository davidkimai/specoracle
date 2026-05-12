# -*- coding: utf-8 -*-
"""
A module for merging configuration settings from multiple sources with defined precedence.
"""

import copy
from typing import Any, Dict, List, Union


def _parse_value(value: str) -> Union[bool, int, List[str], str]:
    """
    Parses a string value from an environment variable into a Python type.

    - "true"/"false" (case-insensitive) become booleans.
    - Comma-separated strings become lists of trimmed, non-empty strings.
    - Strings representing base-10 integers become ints.
    - Other values remain strings.
    """
    cleaned_value = value.strip()
    lower_value = cleaned_value.lower()
