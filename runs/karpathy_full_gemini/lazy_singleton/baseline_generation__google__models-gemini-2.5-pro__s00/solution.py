# -*- coding: utf-8 -*-
"""
A thread-safe, lazy singleton implementation.
"""

import threading
from typing import Callable, TypeVar, Generic

# A generic type variable to represent the type of the singleton instance.
T = TypeVar('T')


class LazySingleton(Generic[T]):
    """
    A thread-safe provider for a lazily-initialized singleton object.

    The object is created by a given 'factory' function on the first call to
    the `get()` method. Subsequent calls, even from concurrent threads, will
    return the same cached object instance.

    This implementation uses the double-checked locking pattern to ensure
    thread safety with minimal performance overhead after the object has been
    initialized.

    Usage:
        # Define a factory function, e.g., for a database connection.
        def create_connection():
            print("Creating a new connection...")
            # In a real application, this would establish a connection.
            return {"host": "localhost", "port": 5432}

        # Create the LazySingleton provider.
        connection_provider = LazySingleton(create_connection)

        # Get the singleton instance. The factory is called only here.
        conn1 = connection_provider.get()

        # Subsequent calls return the cached instance without calling the factory.
        conn2 = connection_provider.get()

        assert conn1 is conn2
    """

    def __init__(self, factory: Callable[[], T]):
        """
        Initializes the LazySingleton with a factory for object creation.

        Args:
            factory: A callable that takes no arguments and returns the
                     object to be managed as a singleton.

        Raises:
            TypeError: If the provided factory is not a callable.
        """
        if not callable(factory):
            raise TypeError("factory must be a callable")
        self._factory = factory
        self._instance: T | None = None
        self._lock = threading.Lock()

    def get(self) -> T:
        """
        Returns the singleton instance, creating it if it doesn't exist.

        This method is safe to call from multiple threads concurrently. The
        factory will be invoked at most once.

        Returns:
            The singleton object instance.
        """
        # First check (optimistic): avoids acquiring the lock on every call
        # after the instance has been created. This is the fast path.
        if self._instance is None:
            # Acquire the lock only when initialization might be needed.
            with self._lock:
                # Second check (pessimistic): ensures that another thread did
                # not create the instance while the current thread was
                # waiting for the lock.
                if self._instance is None:
                    self._instance = self._factory()

        # The instance is guaranteed to be of type T at this point.
        return self._instance
