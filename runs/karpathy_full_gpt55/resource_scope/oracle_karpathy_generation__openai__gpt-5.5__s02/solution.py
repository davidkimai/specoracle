from contextlib import ExitStack


class ResourceScope:
    def __init__(self):
        self._stack = ExitStack()

    def __enter__(self):
        self._stack.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self._stack.__exit__(exc_type, exc_value, traceback)

    def acquire(self, resource):
        self._stack.callback(resource.close)
        return resource
