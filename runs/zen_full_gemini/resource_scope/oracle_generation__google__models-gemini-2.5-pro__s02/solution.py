#
# Per the Zen of Python:
#
# > Simple is better than complex.
# > Readability counts.
# > Errors should never pass silently.
# > There should be one-- and preferably only one --obvious way to do it.
#
# The `contextlib.ExitStack` is the standard library's obvious and correct
# way to manage a dynamic collection of resources that need cleanup. It
# correctly handles the LIFO cleanup order and the complex exception
# propagation required when errors occur both in the main block and during
# cleanup. This implementation uses it as a robust foundation.
#

"""A context manager for handling dynamically acquired resources."""

import contextlib
import sys
import types
import typing

# In Python 3.8+, typing.Protocol is available. For compatibility with older
# versions, we define a simple structural check within the `acquire` method.
# If Python 3.8+ were the minimum target, a Protocol would be more elegant.
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


class Closable(Protocol):
    """A protocol for objects that can be closed."""

    def close(self) -> None:
        ...


T_Closable = typing.TypeVar("T_Closable", bound=Closable)


class ResourceScope:
    """
    A context manager for dynamically acquiring and releasing resources.

    Resources are guaranteed to be closed in the reverse order of acquisition,
    even in the presence of exceptions.

    Usage:
        with ResourceScope() as scope:
            r1 = scope.acquire(open('file1.txt', 'w'))
            r2 = scope.acquire(open('file2.txt', 'w'))
            # ... work with r1 and r2 ...
        # At this point, r2.close() and then r1.close() have been called.
    """

    def __init__(self) -> None:
        """Initializes a new ResourceScope."""
        self._stack = contextlib.ExitStack()

    def acquire(self, resource: T_Closable) -> T_Closable:
        """
        Track a resource, scheduling its `close()` method for context exit.

        Args:
            resource: An object with a callable `close()` method.

        Returns:
            The same resource object that was passed in.

        Raises:
            TypeError: If the provided resource does not have a callable
                       `close` method.
        """
        _validate_resource(resource)
        self._stack.callback(resource.close)
        return resource

    def __enter__(self) -> "ResourceScope":
        """Enter the runtime context for this scope."""
        self._stack.__enter__()
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_value: typing.Optional[BaseException],
        traceback: typing.Optional[types.TracebackType],
    ) -> typing.Optional[bool]:
        """
        Exit the runtime context, closing all acquired resources.

        Delegates exception handling and resource cleanup to the underlying
        `ExitStack`, which ensures correctness.
        """
        return self._stack.__exit__(exc_type, exc_value, traceback)


def _validate_resource(resource: object) -> None:
    """
    Raise a TypeError if the resource does not conform to the Closable protocol.

    This helper ensures that errors from invalid inputs are raised early and
    clearly, rather than during the context exit phase.
    """
    if not hasattr(resource, "close"):
        raise TypeError(f"Resource of type {type(resource).__name__} lacks a 'close' method.")

    if not callable(getattr(resource, "close")):
        raise TypeError(f"The 'close' attribute on resource of type {type(resource).__name__} is not callable.")
