"""
resource_scope.py

A context manager that tracks resources and closes them in reverse acquisition
order on exit, even when an exception occurs.
"""


class ResourceScope:
    """Context manager that closes acquired resources in LIFO order on exit."""

    def __init__(self):
        self._resources = []

    def __enter__(self):
        return self

    def acquire(self, resource):
        """Record *resource* and return it."""
        self._resources.append(resource)
        return resource

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
