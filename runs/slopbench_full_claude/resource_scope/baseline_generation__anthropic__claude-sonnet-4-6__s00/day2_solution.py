"""
resource_scope.py

Implements ResourceScope as a context manager that tracks acquired resources
and closes them in reverse acquisition order upon context exit.
"""


class ResourceScope:
    """
    A context manager that tracks resources acquired via acquire() and
    closes them in reverse acquisition order on exit, even if an exception occurs.
    """

    def __init__(self):
        self._resources = []

    def __enter__(self):
        return self

    def acquire(self, resource):
        """
        Record the resource and return it.

        :param resource: Any object with a close() method.
        :return: The same resource that was passed in.
        """
        self._resources.append(resource)
        return resource

    def release(self, resource):
        """
        Close and remove a specific tracked resource before scope exit.

        :param resource: A previously acquired resource to close and untrack.
        :raises ValueError: If the resource is not currently tracked.
        """
        try:
            self._resources.remove(resource)
        except ValueError:
            raise ValueError(f"Resource {resource!r} is not tracked by this scope")
        resource.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close all tracked resources in reverse acquisition order.
        Exceptions raised during close() are suppressed to allow all resources
        to be closed; the original exception (if any) propagates normally.
        """
        errors = []
        while self._resources:
            resource = self._resources.pop()
            try:
                resource.close()
            except Exception as e:
                errors.append(e)

        # If there was no original exception but closing raised errors,
        # raise the first closing error.
        if exc_type is None and errors:
            raise errors[0]

        # Return False so any original exception propagates.
        return False
