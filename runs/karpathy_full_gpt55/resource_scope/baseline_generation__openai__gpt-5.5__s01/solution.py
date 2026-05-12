from contextlib import ExitStack


def _close_resource(resource):
    resource.close()


class ResourceScope:
    """Context manager that closes acquired resources in reverse order."""

    def __init__(self):
        self._stack = ExitStack()

    def __enter__(self):
        self._stack.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self._stack.__exit__(exc_type, exc_value, traceback)

    def acquire(self, resource):
        """Track *resource* for closing on scope exit and return it."""
        self._stack.callback(_close_resource, resource)
        return resource
