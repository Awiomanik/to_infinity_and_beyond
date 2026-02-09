#!/usr/bin/env python3
"""Utility functions and constants used across the project."""

from __future__ import annotations
import hashlib
from pathlib import Path

# CONSTANTS
RED_TXT: str = "\033[31m"
DEFAULT_TXT: str = "\033[0m"
GREEN_TXT: str = "\033[32m"

BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".tiff", ".bmp", ".webp", ".svg",
    ".pdf", ".eps", ".mp4", ".mov", ".avi", ".mkv", ".webm",
    ".zip", ".tar", ".gz", ".7z", ".rar", ".npy", ".npz", ".h5", ".dat",
}

# FUNCTIONS
def sha256_of_file(path: Path | str, block: int = 1 << 20) -> str:
    """
    Compute SHA-256 hex digest of a file.

    Args:
      path: filesystem path or Path object
      block: read block size (default 1MiB)

    Returns:
      hex string (lowercase) of SHA-256
    """
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(block)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def human_size(n: int | float) -> str:
    """
    Convert bytes to a human-readable string with 2 decimal places.

    Examples:
      human_size(123)       -> "123.00B"
      human_size(2048)      -> "2.00KB"
      human_size(5_242_880) -> "5.00MB"
    """
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024.0:
            return f"{n:.2f}{unit}"
        n /= 1024.0
    return f"{n:.2f}PB"