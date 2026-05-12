"""A context manager for tracking and closing resources."""

import typing
from types import TracebackType

# A type variable for a resource that has a close() method.
# Using a protocol allows for structural subtyping, meaning any object
# with a `close()` method will match, without needing to inherit from a
# specific base class.
class _Closable(typing.Protocol):
    """A protocol for objects that have a close() method."""
    def close(self) -> None:
        ...

_T_Closable = typing.TypeVar("_T_Closable", bound=_Closable)


class ResourceScope:
    """
    A context manager to manage the lifecycle of multiple resources.

    Resources are acquired within the context and are guaranteed to be closed on
    exit, in the reverse order of their acquisition. This ensures a LIFO
    (Last-In, First-Out) cleanup order, which is often necessary for resources
    that depend on each other.

    This context manager correctly handles cleanup even if an exception occurs
    within the `with` block.

    Example:
        with ResourceScope() as scope:
            # db_conn is acquired first
            db_conn = scope.acquire(DatabaseConnection())
            # cursor is acquired second, and likely depends on db_conn
            cursor = scope.acquire(db_conn.cursor())
            cursor.execute("SELECT * FROM users")
        # On exit, cursor.close() is called first, then db_conn.close().
    """

    def __init__(self) -> None:
        self._resources: typing.List[_Closable] = []

    def acquire(self, resource: _T_Closable) -> _T_Closable:
        """
        Records a resource for future cleanup and returns it.

        The resource is added to an internal stack. On context exit, the
        `close()` method of each recorded resource will be called in reverse
        order of acquisition.

        Args:
            resource: The resource to manage. It must have a `close()` method.

        Returns:
            The same resource object that was passed in.
        """
        self._resources.append(resource)
        return resource

    def __enter__(self) -> "ResourceScope":
        """
        Enters the runtime context.

        Returns:
            This `ResourceScope` instance, allowing `acquire` to be called on it.
        """
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_value: typing.Optional[BaseException],
        traceback: typing.Optional[TracebackType],
    ) -> None:
        """
        Exits the runtime context, closing all tracked resources.

        Resources are closed in the reverse order of their acquisition (LIFO).
        If an exception occurred in the `with` block, it is re-raised after
        the cleanup has been performed. This method does not suppress exceptions.
        """
        for resource in reversed(self._resources):
            resource.close()
