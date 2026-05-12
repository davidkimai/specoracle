"""
A context manager for tracking and closing resources in last-in, first-out order.
"""

from __future__ import annotations

from types import TracebackType
from typing import List, Optional, Type, Any


class ResourceScope:
    """
    A context manager to safely manage the lifecycle of multiple resources.

    Resources are acquired and tracked within the scope. On exiting the scope,
    all tracked resources are closed in the reverse order of their acquisition.
    This LIFO (Last-In, First-Out) strategy is suitable for resources that
    depend on each other, ensuring that cleanup happens in the correct order.

    The context manager guarantees that it will attempt to close every acquired
    resource, even if exceptions occur during the cleanup process or within
    the `with` block.

    Example:
        class MockResource:
            def __init__(self, name: str):
                self.name = name
                print(f"Acquired {self.name}")

            def close(self):
                print(f"Closed {self.name}")

            def __repr__(self) -> str:
                return f"<MockResource name='{self.name}'>"

        with ResourceScope() as scope:
            r1 = scope.acquire(MockResource("resource1"))
            r2 = scope.acquire(MockResource("resource2"))
            print("Inside scope, using resources...")
            # On exit, r2.close() is called, then r1.close()
    """

    def __init__(self) -> None:
        """Initializes a new, empty ResourceScope."""
        self._resources: List[Any] = []

    def acquire(self, resource: Any) -> Any:
        """
        Track a resource and return it.

        The tracked resource must have a callable `close()` method, which will be
        invoked upon exiting the scope.

        Args:
            resource: The resource object to track.

        Returns:
            The same resource object that was passed in.

        Raises:
            TypeError: If the `resource` does not have a callable `close` method.
        """
        if not callable(getattr(resource, "close", None)):
            raise TypeError(
                f"Acquired resource of type '{type(resource).__name__}' "
                "must have a callable 'close' method."
            )
        self._resources.append(resource)
        return resource

    def __enter__(self) -> ResourceScope:
        """
        Enters the runtime context for this scope.

        Returns:
            The scope instance, allowing for `acquire()` calls.
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        """
        Exits the context, closing all acquired resources in reverse order.

        If any `close()` call raises an exception, it is captured, and the
        scope continues attempting to close the remaining resources. After all
        attempts, the first captured cleanup exception is re-raised. If no
        cleanup exception occurred, any exception from the `with` block is
        re-raised.
        """
        first_cleanup_exception: Optional[BaseException] = None

        for resource in reversed(self._resources):
            try:
                resource.close()
            except Exception as e:
                if first_cleanup_exception is None:
                    first_cleanup_exception = e

        self._resources.clear()

        if first_cleanup_exception is not None:
            # If cleanup failed, this error is critical. Python 3 automatically
            # chains the original exception (exc_val) to this new one via the
            # __context__ attribute, preserving the full traceback.
            raise first_cleanup_exception

        # Return False to indicate that if an exception occurred within the
        # `with` block (passed as exc_type, exc_val, exc_tb), it should be
        # re-raised by the interpreter. If no exception occurred, this has
        # no effect.
        return False
