"""
Utilities for safe file reading with encoding detection.
Handles the messy real-world case where files might be latin-1, utf-8, etc.
"""

import os
from pathlib import Path


# Encodings to try in order
_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]


def read_file_safe(filepath: str | Path) -> str | None:
    """
    Try to read a file as text, attempting multiple encodings.
    Returns the file content as a string, or None if the file
    cannot be decoded as text (i.e. it is binary).
    """
    filepath = Path(filepath)

    # Quick binary sniff — read first 8KB and look for null bytes
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(8192)
        if b"\x00" in chunk:
            return None  # binary file
    except (OSError, PermissionError):
        return None

    # Try each encoding
    for enc in _ENCODINGS:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
        except (OSError, PermissionError):
            return None

    return None  # all encodings failed


def get_file_size_kb(filepath: str | Path) -> float:
    """Return file size in kilobytes, rounded to 2 decimal places."""
    try:
        size = os.path.getsize(filepath)
        return round(size / 1024, 2)
    except OSError:
        return 0.0


def is_text_file(filepath: str | Path) -> bool:
    """Quick check: can we read this file as text?"""
    return read_file_safe(filepath) is not None
