"""
resource_scope.py

Provides ResourceScope, a context manager that tracks acquired resources
and closes them in reverse acquisition order upon context exit.
"""


class ResourceScope:
    """Context manager that closes acquired resources in reverse order on exit."""

    def __init__(self):
        self._resources = []

    def __enter__(self):
        return self

    def acquire(self, resource):
        """Record a resource and return it."""
        self._resources.append(resource)
        return resource

    def release(self, resource):
        """Close and remove a specific tracked resource before scope exit."""
        try:
            index = self._resources.index(resource)
        except ValueError:
            raise ValueError(f"Resource {resource!r} is not tracked by this scope")
        self._resources.pop(index)
        resource.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        errors = []
        for resource in reversed(self._resources):
            try:
                resource.close()
            except Exception as e:
                errors.append(e)
        self._resources.clear()
        if errors:
            raise errors[0]
        return False
