import sys
from typing import Any, Generic, List, Optional, Protocol, Type, TypeVar


class _Closable(Protocol):
    """A protocol for objects with a no-argument `close` method."""

    def close(self) -> None:
        ...


# A generic type variable for resources, constrained to types with a close() method.
T = TypeVar("T", bound=_Closable)


class ResourceScope(Generic[T]):
    """
    A context manager for tracking and closing resources on context exit.

    Resources are closed in the reverse order of their acquisition. This is
    useful for managing objects with a `close()` method, such as files or
    network connections, ensuring they are cleaned up correctly even in the
    presence of exceptions.
    """

    def __init__(self) -> None:
        """Initializes a new, empty ResourceScope."""
        self._resources: List[T] = []
        self._is_exiting: bool = False

    def acquire(self, resource: T) -> T:
        """
        Records a resource for future cleanup and returns it.

        The tracked resource will have its `close()` method called upon exiting
        the `with` block.

        Args:
            resource: The resource to track. Must have a `close()` method.

        Returns:
            The resource that was passed in.

        Raises:
            RuntimeError: If `acquire` is called while the scope is exiting.
        """
        if self._is_exiting:
            raise RuntimeError(
                "Cannot acquire a resource while the scope is exiting."
            )
        self._resources.append(resource)
        return resource

    def __enter__(self) -> "ResourceScope[T]":
        """Enters the context, returning the scope instance."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> bool:
        """
        Exits the context, closing all tracked resources.

        Resources are closed in reverse acquisition order. If any `close()` call
        raises an exception, closing of subsequent resources continues. The
        first exception raised during cleanup is propagated after all resources
        have been attempted to be closed.
        """
        self._is_exiting = True
        first_cleanup_exception: Optional[BaseException] = None

        for resource in reversed(self._resources):
            try:
                resource.close()
            except Exception as e:
                if first_cleanup_exception is None:
                    first_cleanup_exception = e

        self._resources.clear()

        if first_cleanup_exception is not None:
            raise first_cleanup_exception

        # Return False to indicate that any exception that occurred within the
        # `with` block should be re-raised by the context manager.
        return False
