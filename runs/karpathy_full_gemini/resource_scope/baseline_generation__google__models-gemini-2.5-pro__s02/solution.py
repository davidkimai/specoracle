"""
A context manager for tracking and closing resources in a specific order.
"""

from typing import Any, List, Optional, Type, TypeVar, TracebackType

# A type variable for a generic resource.
# We don't constrain it to have a `close` method here, as the implementation
# will check for it
