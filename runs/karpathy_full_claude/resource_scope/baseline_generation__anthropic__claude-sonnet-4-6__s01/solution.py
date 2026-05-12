class ResourceScope:
    def __init__(self):
        self._resources = []

    def __enter__(self):
        return self

    def acquire(self, resource):
        self._resources.append(resource)
        return resource

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
