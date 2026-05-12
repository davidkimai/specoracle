"""
A module for managing the lifecycle of resources within a specific scope.
"""

import contextlib
from typing import Protocol, TypeVar, Any, Type, Optional


class Closable(Protocol):
    """A protocol for resources that have a zero-argument `close` method."""

    def close(self) -> None:
        """Closes the resource."""
        ...


T_Closable = TypeVar("T_Closable", bound=Closable)


class ResourceScope:
    """
    A context manager for tracking and closing resources in a LIFO order.

    This class ensures that all acquired resources are closed correctly on context
    exit, even in the presence of exceptions. Resources are closed in the reverse
    order of their acquisition.
    """

    def __init__(self) -> None:
        """Initializes a new ResourceScope."""
        self._exit_stack = contextlib.ExitStack()

    def __enter__(self) -> "ResourceScope":
        """Enters the context, preparing it to manage resources."""
        self._exit_stack.__enter__()
        return self

    def acquire(self, resource: T_Closable) -> T_Closable:
        """
        Records a resource for future cleanup and returns it.

        The resource's `close` method will be called when the scope is exited.

        Args:
            resource: An object that conforms to the `Closable` protocol.

        Returns:
            The same resource object that was passed in.
        """
        self._exit_stack.callback(resource.close)
        return resource

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> Optional[bool]:
        """
        Exits the context, closing all acquired resources in reverse order.
        """
        return self._exit_stack.__exit__(exc_type, exc_value, traceback)
