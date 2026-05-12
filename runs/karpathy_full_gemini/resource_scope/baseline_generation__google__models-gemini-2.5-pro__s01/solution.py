"""
A module for managing a dynamic scope of resources that need cleanup.
"""

from types import TracebackType
from typing import Any, Generic, List, Optional, Type, TypeVar

_ResourceT = TypeVar("_ResourceT")


class ResourceScope:
    """
    A context manager for dynamically acquiring and releasing resources.

    Resources are guaranteed to be closed in the reverse order of their
    acquisition, even in the event of exceptions. This is similar in concept
    to contextlib.ExitStack but implemented as a standalone class.

    Usage:
        with ResourceScope() as scope:
            f1 = scope.acquire(open("file1.txt", "w"))
            f2 = scope.acquire(open("file2.txt", "w"))
            # ... do work with f1 and f2 ...
        # f2.close() is called, then f1.close() is called, automatically.
    """

    def __init__(self) -> None:
        """Initializes a new, empty ResourceScope."""
        self._resources: List[Any] = []

    def __enter__(self) -> "ResourceScope":
        """Enters the context, returning self for acquiring resources."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        """
        Exits the context, closing all acquired resources.

        Closes resources in LIFO (Last-In, First-Out) order. If exceptions
        occur during the closing of resources, it attempts to close all
        remaining resources. The original exception from the `with` block (if
        any) is preserved and re-raised in preference to any exceptions that
        occur during cleanup.

        Args:
            exc_type: The type of the exception raised in the `with` block.
            exc_value: The exception instance raised in the `with` block.
            traceback: The traceback for the exception.

        Returns:
            False, to indicate that any exception raised in the `with` block
            should be propagated.
        """
        closing_exception: Optional[BaseException] = None

        while self._resources:
            resource = self._resources.pop()
            try:
                # The contract is that acquired resources have a `close()` method.
                resource.close()
            except Exception as e:
                if closing_exception is None:
                    closing_exception = e

        if exc_type is None and closing_exception is not None:
            # If the `with` block completed successfully but an exception
            # occurred during cleanup, raise the cleanup exception.
            raise closing_exception

        # Returning False ensures that if an exception occurred in the `with`
        # block (exc_type is not None), it is re-raised. Any `closing_exception`
        # is suppressed in favor of the original one.
        return False

    def acquire(self, resource: _ResourceT) -> _ResourceT:
        """
        Acquires and records a resource to be closed upon exiting the scope.

        The resource is expected to have a `close()` method that can be called
        without arguments.

        Args:
            resource: The resource to acquire and manage.

        Returns:
            The same resource that was passed in, to allow for convenient
            assignment.
        """
        self._resources.append(resource)
        return resource
