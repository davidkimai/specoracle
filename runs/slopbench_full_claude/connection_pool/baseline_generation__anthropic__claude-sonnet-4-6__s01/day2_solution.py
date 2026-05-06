#!/usr/bin/env python3
"""
Module providing a thread-safe generic connection pool.
"""

import threading
import time
import logging
from typing import Any, Callable, Optional, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PoolExhaustedError(Exception):
    """Raised when the connection pool is exhausted and no connection is available."""
    pass


class ConnectionPool:
    """
    A thread-safe generic connection pool.
    
    Manages a pool of connections created by a factory function, with support
    for maximum pool size, connection validation, and idle connection cleanup.
    """

    def __init__(
        self,
        factory: Callable[[], Any],
        max_size: int = 10,
        min_size: int = 0,
        max_idle_time: Optional[float] = None,
        connection_timeout: float = 30.0,
        validate_on_borrow: bool = False,
        validator: Optional[Callable[[Any], bool]] = None,
        health_check: Optional[Callable[[Any], bool]] = None,
    ):
        """
        Initialize the connection pool.

        Args:
            factory: Callable that creates new connections
            max_size: Maximum number of connections in the pool
            min_size: Minimum number of connections to maintain
            max_idle_time: Maximum time (seconds) a connection can be idle before cleanup
            connection_timeout: Timeout (seconds) when waiting for a connection
            validate_on_borrow: Whether to validate connections when borrowing
            validator: Optional callable to validate a connection, returns True if valid
            health_check: Optional callable to health-check an idle connection before
                          returning it to the caller; if it returns False the connection
                          is closed and the pool continues looking for another one.
        """
        if max_size < 1:
            raise ValueError("max_size must be at least 1")
        if min_size < 0:
            raise ValueError("min_size must be non-negative")
        if min_size > max_size:
            raise ValueError("min_size cannot exceed max_size")

        self._factory = factory
        self._max_size = max_size
        self._min_size = min_size
        self._max_idle_time = max_idle_time
        self._connection_timeout = connection_timeout
        self._validate_on_borrow = validate_on_borrow
        self._validator = validator
        self._health_check = health_check

        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        
        # Pool of idle connections with metadata
        self._idle_connections: List[dict] = []
        # Track total connections (idle + active)
        self._total_connections: int = 0
        self._active_connections: int = 0
        self._closed: bool = False

        # Initialize minimum connections
        self._initialize_min_connections()

    def _initialize_min_connections(self):
        """Create the minimum number of connections."""
        for _ in range(self._min_size):
            try:
                conn = self._create_connection()
                self._idle_connections.append({
                    'connection': conn,
                    'created_at': time.monotonic(),
                    'last_used': time.monotonic(),
                })
            except Exception as e:
                logger.warning(f"Failed to create initial connection: {e}")

    def _create_connection(self) -> Any:
        """Create a new connection using the factory."""
        conn = self._factory()
        self._total_connections += 1
        logger.debug(f"Created new connection. Total: {self._total_connections}")
        return conn

    def _is_valid(self, conn: Any) -> bool:
        """Validate a connection."""
        if self._validator is not None:
            try:
                return self._validator(conn)
            except Exception:
                return False
        return True

    def _is_healthy(self, conn: Any) -> bool:
        """Run the health check on a connection, if one is configured."""
        if self._health_check is None:
            return True
        try:
            return bool(self._health_check(conn))
        except Exception:
            return False

    def _close_connection(self, conn: Any):
        """Attempt to close a connection."""
        try:
            if hasattr(conn, 'close'):
                conn.close()
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")
        finally:
            with self._lock:
                self._total_connections = max(0, self._total_connections - 1)

    def acquire(self, timeout: Optional[float] = None) -> Any:
        """
        Acquire a connection from the pool.

        Args:
            timeout: Optional timeout override (uses connection_timeout if not specified)

        Returns:
            A connection object

        Raises:
            PoolExhaustedError: If no connection is available within the timeout
            RuntimeError: If the pool is closed
        """
        if self._closed:
            raise RuntimeError("Connection pool is closed")

        deadline = time.monotonic() + (timeout if timeout is not None else self._connection_timeout)

        with self._not_empty:
            while True:
                if self._closed:
                    raise RuntimeError("Connection pool is closed")

                # Try to get an idle connection
                while self._idle_connections:
                    entry = self._idle_connections.pop(0)
                    conn = entry['connection']

                    # Check if connection has exceeded max idle time
                    if self._max_idle_time is not None:
                        idle_duration = time.monotonic() - entry['last_used']
                        if idle_duration > self._max_idle_time:
                            logger.debug(f"Discarding connection idle for {idle_duration:.1f}s")
                            self._close_connection(conn)
                            continue

                    # Validate connection if required
                    if self._validate_on_borrow and not self._is_valid(conn):
                        logger.debug("Discarding invalid connection")
                        self._close_connection(conn)
                        continue

                    # Health-check the idle connection if a checker is configured
                    if not self._is_healthy(conn):
                        logger.debug("Discarding unhealthy connection (health_check returned False)")
                        self._close_connection(conn)
                        continue

                    self._active_connections += 1
                    logger.debug(f"Acquired existing connection. Active: {self._active_connections}")
                    return conn

                # No idle connections available; try to create a new one
                if self._total_connections < self._max_size:
                    try:
                        conn = self._create_connection()
                        self._active_connections += 1
                        logger.debug(f"Acquired new connection. Active: {self._active_connections}")
                        return conn
                    except Exception as e:
                        logger.error(f"Failed to create connection: {e}")
                        raise

                # Pool is exhausted; wait for a connection to be released
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise PoolExhaustedError(
                        f"Connection pool exhausted (max_size={self._max_size}). "
                        f"No connection available within timeout."
                    )

                logger.debug(f"Pool exhausted, waiting up to {remaining:.1f}s for a connection")
                self._not_empty.wait(timeout=remaining)

    def release(self, conn: Any):
        """
        Return a connection to the pool.

        Args:
            conn: The connection to return
        """
        if self._closed:
            self._close_connection(conn)
            return

        with self._not_empty:
            self._active_connections = max(0, self._active_connections - 1)

            # Validate connection before returning to pool
            if not self._is_valid(conn):
                logger.debug("Discarding invalid connection on release")
                self._close_connection(conn)
                self._not_empty.notify_all()
                return

            # Return to pool if we haven't exceeded max_size
            if len(self._idle_connections) < self._max_size:
                self._idle_connections.append({
                    'connection': conn,
                    'created_at': time.monotonic(),  # approximate
                    'last_used': time.monotonic(),
                })
                logger.debug(f"Released connection back to pool. Idle: {len(self._idle_connections)}")
                self._not_empty.notify()
            else:
                # Pool is full, close the connection
                logger.debug("Pool full, closing released connection")
                self._close_connection(conn)
                self._not_empty.notify_all()

    @contextmanager
    def connection(self, timeout: Optional[float] = None):
        """
        Context manager for acquiring and releasing connections.

        Usage:
            with pool.connection() as conn:
                # use conn
        """
        conn = self.acquire(timeout=timeout)
        try:
            yield conn
        except Exception:
            # On exception, we still return the connection but could mark it invalid
            raise
        finally:
            self.release(conn)

    def cleanup_idle(self, max_idle_time: Optional[float] = None):
        """
        Remove and close connections that have been idle too long.

        Args:
            max_idle_time: Maximum idle time in seconds. Uses pool's max_idle_time if not specified.
        """
        idle_threshold = max_idle_time if max_idle_time is not None else self._max_idle_time
        if idle_threshold is None:
            return

        now = time.monotonic()
        connections_to_close = []

        with self._lock:
            active_idle = []
            for entry in self._idle_connections:
                idle_duration = now - entry['last_used']
                if idle_duration > idle_threshold:
                    connections_to_close.append(entry['connection'])
                    self._total_connections = max(0, self._total_connections - 1)
                else:
                    active_idle.append(entry)
            self._idle_connections = active_idle

        # Close connections outside the lock
        for conn in connections_to_close:
            try:
                if hasattr(conn, 'close'):
                    conn.close()
            except Exception as e:
                logger.warning(f"Error closing idle connection: {e}")

        if connections_to_close:
            logger.info(f"Cleaned up {len(connections_to_close)} idle connections")

    # ------------------------------------------------------------------
    # evict_idle: required by the original functional contract
    # ------------------------------------------------------------------
    def evict_idle(self, max_idle_seconds: float):
        """
        Close and remove idle connections older than *max_idle_seconds*.

        This is an alias for cleanup_idle() that matches the contract
        described in the original requirements.

        Args:
            max_idle_seconds: Connections idle longer than this many seconds
                              will be closed and removed from the pool.
        """
        self.cleanup_idle(max_idle_time=max_idle_seconds)

    def close(self):
        """
        Close all connections and shut down the pool.
        """
        with self._not_empty:
            self._closed = True
            idle_connections = [entry['connection'] for entry in self._idle_connections]
            self._idle_connections.clear()
            self._not_empty.notify_all()

        # Close all idle connections outside the lock
        for conn in idle_connections:
            try:
                if hasattr(conn, 'close'):
                    conn.close()
            except Exception as e:
                logger.warning(f"Error closing connection during pool shutdown: {e}")

        logger.info("Connection pool closed")

    @property
    def size(self) -> int:
        """Total number of connections (idle + active)."""
        with self._lock:
            return self._total_connections

    @property
    def idle_count(self) -> int:
        """Number of idle connections."""
        with self._lock:
            return len(self._idle_connections)

    @property
    def active_count(self) -> int:
        """Number of active (borrowed) connections."""
        with self._lock:
            return self._active_connections

    @property
    def max_size(self) -> int:
        """Maximum pool size."""
        return self._max_size

    @property
    def is_closed(self) -> bool:
        """Whether the pool has been closed."""
        return self._closed

    def __repr__(self) -> str:
        return (
            f"ConnectionPool(max_size={self._max_size}, "
            f"total={self._total_connections}, "
            f"idle={len(self._idle_connections)}, "
            f"active={self._active_connections}, "
            f"closed={self._closed})"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
