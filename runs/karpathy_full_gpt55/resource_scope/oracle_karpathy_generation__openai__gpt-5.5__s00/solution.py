class ResourceScope:
    def __init__(self):
        self._resources = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        while self._resources:
            resource = self._resources.pop()
            resource.close()
        return False

    def acquire(self, resource):
        self._resources.append(resource)
        return resource
