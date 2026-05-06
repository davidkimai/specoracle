"""
resource_scope.py

A context manager that tracks acquired resources and closes them in
reverse acquisition order on exit, even when an exception occurs.
"""


class ResourceScope:
    """Context manager that closes tracked resources in LIFO order on exit."""

    def __init__(self):
        self._resources = []

    def __enter__(self):
        return self

    def acquire(self, resource):
        """Record *resource* and return it."""
        self._resources.append(resource)
        return resource

    def release(self, resource):
        """Close and remove a specific tracked resource before scope exit.

        Raises ValueError if *resource* is not currently tracked.
        """
        try:
            self._resources.remove(resource)
        except ValueError:
            raise ValueError(f"Resource {resource!r} is not tracked by this scope")
        resource.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        errors = []
        for resource in reversed(self._resources):
            try:
                resource.close()
            except Exception as err:  # noqa: BLE001
                errors.append(err)
        self._resources.clear()
        if errors:
            raise errors[0]
        return False  # do not suppress the original exception
