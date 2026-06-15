"""
Directory traverser.

Walks a local directory recursively, filters out noise (binary files,
dependency folders, build artifacts), and returns metadata for every
parseable source file it finds.
"""

import os
from pathlib import Path
from dataclasses import dataclass

from app.utils.language_map import SKIP_DIRS, SKIP_EXTENSIONS, get_language
from app.utils.file_utils import get_file_size_kb, read_file_safe


@dataclass
class FileEntry:
    """Lightweight record for a single discovered source file."""
    abs_path: str        # absolute path on disk
    rel_path: str        # path relative to the repo root (used as node ID)
    filename: str        # basename only, e.g. "parser.py"
    extension: str       # e.g. ".py"
    language: str        # e.g. "python"
    size_kb: float
    content: str         # full text content


def traverse(root: str) -> list[FileEntry]:
    """
    Walk *root* recursively and return a FileEntry for every
    source file that passes all filters.

    Raises:
        ValueError: if root does not exist or is not a directory.
    """
    root_path = Path(root).resolve()

    if not root_path.exists():
        raise ValueError(f"Path does not exist: {root}")
    if not root_path.is_dir():
        raise ValueError(f"Path is not a directory: {root}")

    entries: list[FileEntry] = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Prune skip dirs IN PLACE so os.walk won't descend into them
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not d.startswith(".")
        ]

        for filename in filenames:
            abs_path = Path(dirpath) / filename
            ext = abs_path.suffix

            # Skip non-source extensions
            if ext in SKIP_EXTENSIONS:
                continue

            # Skip files with no recognised extension
            lang_info = get_language(ext)
            if lang_info is None:
                continue

            # Skip files that are too large (> 500 KB) — they're usually
            # generated or minified and would blow up the AI prompt
            size_kb = get_file_size_kb(abs_path)
            if size_kb > 500:
                continue

            # Try to read as text
            content = read_file_safe(abs_path)
            if content is None:
                continue  # binary or unreadable

            rel_path = str(abs_path.relative_to(root_path))
            # Normalise to forward slashes on all platforms
            rel_path = rel_path.replace("\\", "/")

            entries.append(
                FileEntry(
                    abs_path=str(abs_path),
                    rel_path=rel_path,
                    filename=filename,
                    extension=ext,
                    language=lang_info["name"],
                    size_kb=size_kb,
                    content=content,
                )
            )

    return entries
