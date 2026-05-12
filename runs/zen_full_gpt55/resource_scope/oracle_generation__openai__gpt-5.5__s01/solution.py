from contextlib import ExitStack

__all__ = ["ResourceScope"]


def _get_close_method(resource):
    close = getattr(resource, "close", None)
    if not callable(close):
        resource_type = type(resource).__name__
        raise TypeError(
            f"{resource_type} resource must provide a callable close() method"
        )
    return close


def _close_resource(resource):
    _get_close_method(resource)()


class ResourceScope:
    """Context manager that closes acquired resources in reverse order."""

    def __init__(self):
        self._exit_stack = ExitStack()
        self._entered = False
        self._closed = False

    def __enter__(self):
        if self._closed:
            raise RuntimeError("ResourceScope cannot be entered after it is closed")
        if self._entered:
            raise RuntimeError("ResourceScope cannot be entered more than once")
        self._entered = True
        self._exit_stack.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._closed = True
        self._entered = False
        return self._exit_stack.__exit__(exc_type, exc_value, traceback)

    def acquire(self, resource):
        if self._closed:
            raise RuntimeError("ResourceScope is closed")
        _get_close_method(resource)
        self._exit_stack.callback(_close_resource, resource)
        return resource
