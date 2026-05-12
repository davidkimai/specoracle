class ResourceScope:
    def __init__(self):
        self._resources = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        raised = None

        while self._resources:
            resource = self._resources.pop()
            try:
                resource.close()
            except BaseException as error:
                if raised is None:
                    raised = error

        if raised is not None:
            raise raised

        return False

    def acquire(self, resource):
        self._resources.append(resource)
        return resource
