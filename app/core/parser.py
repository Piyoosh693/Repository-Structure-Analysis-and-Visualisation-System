"""
Dependency parser.

Given a list of FileEntry objects, this module:
1. Extracts raw import strings from each file using language-specific regex.
2. Attempts to resolve each import to an actual file in the repo.
3. Returns a list of (source_rel_path, target_rel_path) edge tuples.

Resolution is best-effort — unresolved imports (stdlib, third-party) are
silently dropped. Only edges between two files that EXIST in the repo are kept.
"""

import re
from pathlib import Path, PurePosixPath

from app.core.traverser import FileEntry
from app.utils.language_map import get_language


def extract_imports(entry: FileEntry) -> list[str]:
    """
    Run all regex patterns for the file's language against its content.
    Returns a list of raw import strings (module names or relative paths).
    """
    lang_info = get_language(entry.extension)
    if lang_info is None:
        return []

    raw_imports: list[str] = []
    for pattern in lang_info["patterns"]:
        for match in re.finditer(pattern, entry.content, re.MULTILINE):
            captured = match.group(1).strip()
            if captured:
                raw_imports.append(captured)

    return raw_imports


def _resolve_python(raw: str, source_entry: FileEntry, index: dict[str, str]) -> str | None:
    """
    Resolve a Python import string to a rel_path.
    Handles both absolute (from root) and relative (leading dots) imports.

    Strategy:
      1. Convert dotted module path → file path candidate
      2. Look for an exact match in the index
      3. Also try with /__init__.py suffix (package import)
    """
    source_dir = str(PurePosixPath(source_entry.rel_path).parent)

    # Relative import: leading dots
    if raw.startswith("."):
        dots = len(raw) - len(raw.lstrip("."))
        module_part = raw.lstrip(".")
        # Walk up `dots` levels from source_dir
        parts = source_dir.split("/") if source_dir != "." else []
        parts = parts[:max(0, len(parts) - (dots - 1))]
        if module_part:
            parts += module_part.split(".")
        candidate = "/".join(parts)
    else:
        candidate = raw.replace(".", "/")

    # Try direct file match
    for suffix in [".py", "/__init__.py"]:
        key = candidate + suffix
        if key in index:
            return key

    # Try matching as a suffix (handles when source is in a subdirectory
    # and the import is repo-root-relative but written without leading dot)
    for rel_path in index:
        if rel_path.endswith(candidate + ".py") or rel_path.endswith(candidate + "/__init__.py"):
            return rel_path

    return None


def _resolve_js_ts(raw: str, source_entry: FileEntry, index: dict[str, str]) -> str | None:
    """
    Resolve a JS/TS relative import path to a rel_path.
    Handles: ./foo, ../bar, ./components/Button (no extension).
    """
    if not raw.startswith("."):
        return None  # third-party — skip

    source_dir = str(PurePosixPath(source_entry.rel_path).parent)
    # Resolve the relative path against the source file's directory
    try:
        resolved = str(PurePosixPath(source_dir) / raw)
        # Normalise (remove .. etc.) — PurePosixPath doesn't resolve ..
        # so we do it manually
        parts = []
        for part in resolved.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part != ".":
                parts.append(part)
        resolved = "/".join(parts)
    except Exception:
        return None

    js_ts_exts = [".js", ".jsx", ".ts", ".tsx"]

    # Try with each extension appended
    for ext in js_ts_exts:
        key = resolved + ext
        if key in index:
            return key

    # Try exact match (import already had extension)
    if resolved in index:
        return resolved

    # Try index.* inside the resolved path (directory import)
    for ext in js_ts_exts:
        key = resolved + "/index" + ext
        if key in index:
            return key

    return None


def _resolve_c_cpp(raw: str, source_entry: FileEntry, index: dict[str, str]) -> str | None:
    """
    Resolve a C/C++ local #include "file.h" to a rel_path.
    Looks relative to the including file's directory first, then repo root.
    """
    source_dir = str(PurePosixPath(source_entry.rel_path).parent)

    candidates = [
        f"{source_dir}/{raw}",  # relative to source
        raw,                     # relative to repo root
    ]

    for c in candidates:
        # Normalise
        parts = []
        for part in c.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part != ".":
                parts.append(part)
        key = "/".join(parts)
        if key in index:
            return key

    return None


def _resolve_java(raw: str, index: dict[str, str]) -> str | None:
    """
    Resolve a Java import statement like com.example.utils.Parser
    to a rel_path like src/main/java/com/example/utils/Parser.java
    """
    candidate = raw.replace(".", "/") + ".java"
    if candidate in index:
        return candidate
    # Try suffix match
    for rel_path in index:
        if rel_path.endswith(candidate):
            return rel_path
    return None


def build_edges(entries: list[FileEntry]) -> list[tuple[str, str]]:
    """
    Given all FileEntry objects, extract and resolve all dependencies.
    Returns a list of (source_rel_path, target_rel_path) tuples where
    both ends are known files in the repo.

    Deduplicates edges.
    """
    # Build lookup index: rel_path → rel_path (for fast membership testing)
    index: dict[str, str] = {e.rel_path: e.rel_path for e in entries}

    edges: set[tuple[str, str]] = set()

    for entry in entries:
        raw_imports = extract_imports(entry)

        for raw in raw_imports:
            target = None

            if entry.language == "python":
                target = _resolve_python(raw, entry, index)
            elif entry.language in ("javascript", "typescript", "jsx", "tsx"):
                target = _resolve_js_ts(raw, entry, index)
            elif entry.language in ("c", "cpp", "c_header", "cpp_header"):
                target = _resolve_c_cpp(raw, entry, index)
            elif entry.language == "java":
                target = _resolve_java(raw, index)

            if target and target != entry.rel_path:
                edges.add((entry.rel_path, target))

    return list(edges)
