#
# Copyright (c) 2023, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.
#

"""
A module for managing a collection of resources within a specific scope.
"""

from __future__ import annotations

from types import TracebackType
from typing import List, Optional, Protocol, Type, TypeVar


class _Closable(Protocol):
    """A protocol defining an object with a no-argument close() method."""

    def close(self) -> None:
        ...


_T = TypeVar("_T", bound=_Closable)


class ResourceScope:
    """
    A context manager for safely managing resources that need to be closed.

    Resources are acquired within the scope and are guaranteed to be closed
    upon exiting the scope, even in the event of an exception. Resources are
    closed in the reverse order of their acquisition.

    This pattern is useful for managing multiple resources like files or
    network connections without nesting multiple `with` statements.

    Example:
        class MockResource:
            def __init__(self, name: str):
                self.name = name
                print(f"Acquiring {self.name}")

            def close(self) -> None:
                print(f"Closing {self.name}")

        with ResourceScope() as scope:
            r1 = scope.acquire(MockResource("resource1"))
            r2 = scope.acquire(MockResource("resource2"))
            print("Inside the scope")
        # Output:
        # Acquiring resource1
        # Acquiring resource2
        # Inside the scope
        # Closing resource2
        # Closing resource1
    """

    def __init__(self) -> None:
        """Initializes a new, empty ResourceScope."""
        self._resources: list[_Closable] = []

    def acquire(self, resource: _T) -> _T:
        """
        Track a resource to be closed upon exiting the scope.

        The provided resource must have a `close()` method that takes no
        arguments.

        Args:
            resource: The resource object to manage.

        Returns:
            The same resource object that was passed in.
        """
        self._resources.append(resource)
        return resource

    def __enter__(self) -> ResourceScope:
        """
        Enters the context, returning the scope instance.

        Returns:
            The ResourceScope instance itself.
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        """
        Exits the context, closing all acquired resources.

        Resources are closed in the reverse order of acquisition (LIFO).
        If an exception occurs while closing a resource, the cleanup process
        continues with the remaining resources. If one or more exceptions
        occur during cleanup, the first one encountered is raised after all
        resources have been attempted to be closed.

        An exception during the cleanup phase will suppress any original
        exception that occurred within the `with` block.

        Args:
            exc_type: The type of the exception raised in the `with` block.
            exc_val: The exception instance raised in the `with` block.
            exc_tb: The traceback for the exception.

        Returns:
            False, to ensure that any exception from the `with` block is
            re-raised if not superseded by an exception during cleanup.
        """
        first_cleanup_exception: Optional[BaseException] = None

        for resource in reversed(self._resources):
            try:
                resource.close()
            except Exception as e:
                if first_cleanup_exception is None:
                    # Capture the first exception encountered during cleanup.
                    first_cleanup_exception = e

        # After attempting to close everything, if a cleanup exception was
        # captured, raise it. This will suppress the original exception from
        # the 'with' block, which is standard behavior for exceptions in
        # __exit__.
        if first_cleanup_exception is not None:
            raise first_cleanup_exception

        # Returning False ensures that if an exception occurred in the 'with'
        # block (and not during cleanup), it is re-raised.
        return False
