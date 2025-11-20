"""Atomic File Locking for JSON State Management (GAD-701)"""

import fcntl
import json
from pathlib import Path
from typing import Any


def atomic_read_json(path: Path) -> dict[str, Any]:
    """
    Read JSON with file lock (prevents race conditions)
    """
    with open(path) as f:
        # Using a shared lock for reading to allow multiple readers
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        try:
            # Must seek(0) to ensure read is from the start after the lock is acquired
            f.seek(0)
            return json.load(f)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def atomic_write_json(path: Path, data: dict[str, Any]):
    """
    Atomic JSON write (lock -> temp file -> replace)

    This prevents:
    - Race conditions (via exclusive lock on the temporary file)
    - Corrupted JSON (via temp file)
    """
    temp_path = path.with_suffix(".tmp")

    # Write to temp file
    with open(temp_path, "w") as f:
        # Exclusive lock on the temporary file
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(data, f, indent=2, default=str)
            f.flush()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # Atomic replace (renaming is atomic on POSIX filesystems)
    temp_path.replace(path)
