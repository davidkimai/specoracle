class ResourceScope:
    def __init__(self):
        self._resources = []

    def __enter__(self):
        return self

    def acquire(self, resource):
        self._resources.append(resource)
        return resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        for resource in reversed(self._resources):
            resource.close()
        return False
