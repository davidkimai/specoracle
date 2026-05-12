"""A context manager for dynamically managing a collection of resources."""


class ResourceScope:
    """
    A context manager to track and close resources in a scoped block.

    Resources are closed in the reverse order of their acquisition. This is
    useful for managing a dynamic number of resources that need to be cleaned
    up reliably, such as a set of file handles or network connections.

    Example:
        with ResourceScope() as scope:
            f1 = scope.acquire(open('file1.txt', 'w'))
            f2 = scope.acquire(open('file2.txt', 'w'))
            f1.write('hello')
            f2.write('world')
        # f2 is closed, then f1 is closed, even if an error occurred in the block.
    """

    def __init__(self):
        """Initializes a new, empty ResourceScope."""
        self._resources = []

    def acquire(self, resource):
        """
        Tracks a resource to be closed upon exiting the scope.

        The resource must have a callable `close` method.

        Args:
            resource: The resource object to manage.

        Returns:
            The provided resource, unchanged.

        Raises:
            TypeError: If the resource does not have a
