"""Helpers for acquiring locks on FMU directories."""

from __future__ import annotations

import contextlib
import fcntl
import json
import logging
import os
import socket
import stat
from datetime import UTC, datetime
from pathlib import Path
from typing import TextIO

logger = logging.getLogger(__name__)

_WRITE_MASK = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
_EXEC_MASK = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH


class FMULockPermissionError(PermissionError):
    """Raised when an .fmu directory cannot be locked due to permissions."""


def require_directory_write_access(directory: Path) -> None:
    """Ensures a directory is writable for lock acquisition."""

    mode = directory.stat().st_mode
    if (mode & _WRITE_MASK) == 0 or (mode & _EXEC_MASK) == 0:
        raise FMULockPermissionError(f"Permission denied accessing {directory}")


class FMUDirectoryLock:
    """Represents an exclusive lock on a project .fmu directory."""

    def __init__(self, directory: Path | str) -> None:
        self._directory = Path(directory)
        self._lock_path = self._directory / ".lock"
        self._handle: TextIO | None = None

    @property
    def directory(self) -> Path:
        """The locked .fmu directory."""

        return self._directory

    @property
    def path(self) -> Path:
        """Path to the lock file."""

        return self._lock_path

    @property
    def is_acquired(self) -> bool:
        """Whether the lock is currently acquired."""

        return self._handle is not None

    def acquire(self, session_id: str) -> bool:
        """Attempts to acquire the lock for a session.

        Args:
            session_id: Identifier of the session acquiring the lock.

        Returns:
            ``True`` if the lock was acquired, ``False`` if it is already locked
            by another process.

        Raises:
            OSError: If the lock could not be created for other reasons (e.g.
                permission errors).
        """

        if self._handle is not None:
            logger.debug(
                "Session %s already holds lock at %s", session_id, self._lock_path
            )
            return True

        require_directory_write_access(self._directory)
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_file = self._lock_path.open("a+", encoding="utf-8")

        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lock_file.close()
            logger.debug("Lock at %s already acquired", self._lock_path)
            return False
        except Exception:
            lock_file.close()
            raise

        try:
            lock_file.seek(0)
            lock_file.truncate()
            payload = {
                "session_id": session_id,
                "pid": os.getpid(),
                "hostname": socket.gethostname(),
                "acquired_at": datetime.now(UTC).isoformat(),
            }
            json.dump(payload, lock_file)
            lock_file.write("\n")
            lock_file.flush()
            os.fsync(lock_file.fileno())
        except Exception:
            with contextlib.suppress(OSError):
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
            raise

        self._handle = lock_file
        logger.debug("Acquired lock at %s for session %s", self._lock_path, session_id)
        return True

    def release(self) -> None:
        """Releases the lock if it is held."""

        if self._handle is None:
            return

        try:
            fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
        finally:
            try:
                self._handle.close()
            finally:
                self._handle = None
                with contextlib.suppress(FileNotFoundError):
                    self._lock_path.unlink()
                logger.debug("Released lock at %s", self._lock_path)

    def __del__(self) -> None:  # pragma: no cover - best effort cleanup
        with contextlib.suppress(Exception):
            self.release()
