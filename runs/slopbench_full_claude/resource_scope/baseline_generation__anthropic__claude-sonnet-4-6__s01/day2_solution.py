class ResourceScope:
    def __init__(self):
        self._resources = []

    def __enter__(self):
        return self

    def acquire(self, resource):
        self._resources.append(resource)
        return resource

    def release(self, resource):
        if resource not in self._resources:
            raise ValueError("Resource is not tracked by this scope")
        resource.close()
        self._resources.remove(resource)

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
