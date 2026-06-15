"""
Cache service.

Persists AI summaries to disk as a JSON file, keyed by the SHA-256
hash of the file's content. This means:
  - Cache hits are instant (disk read).
  - Cache automatically invalidates when the file changes (new hash).
  - No manual TTL or expiry needed.

Cache file location: backend/cache/summaries.json
"""

import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

# Resolve cache file path relative to this file's location
_CACHE_DIR = Path(__file__).parent.parent.parent / "cache"
_CACHE_FILE = _CACHE_DIR / "summaries.json"


def _load_cache() -> dict:
    """Load the cache from disk. Returns empty dict on any error."""
    try:
        if _CACHE_FILE.exists():
            with open(_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def _save_cache(data: dict) -> None:
    """Write the cache dict to disk atomically (write to temp, rename)."""
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = _CACHE_FILE.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        tmp.replace(_CACHE_FILE)
    except OSError:
        # Non-fatal: cache write failure should not crash the API
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def compute_hash(content: str) -> str:
    """Return the SHA-256 hex digest of the given content string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def get_cached_summary(content_hash: str) -> str | None:
    """
    Look up a summary by content hash.
    Returns the summary string if found, else None.
    """
    cache = _load_cache()
    entry = cache.get(content_hash)
    if entry and isinstance(entry, dict):
        return entry.get("summary")
    return None


def set_cached_summary(content_hash: str, summary: str, filepath: str = "") -> None:
    """
    Store a summary in the cache under the given content hash.
    Adds a timestamp and the filepath for debugging purposes.
    """
    cache = _load_cache()
    cache[content_hash] = {
        "summary": summary,
        "filepath": filepath,
        "cached_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_cache(cache)


def cache_stats() -> dict:
    """Return basic stats about the current cache (for the /api/cache endpoint)."""
    cache = _load_cache()
    return {
        "total_entries": len(cache),
        "cache_file": str(_CACHE_FILE),
        "size_kb": round(_CACHE_FILE.stat().st_size / 1024, 2) if _CACHE_FILE.exists() else 0,
    }


def clear_cache() -> int:
    """Wipe all entries. Returns number of entries cleared."""
    cache = _load_cache()
    count = len(cache)
    _save_cache({})
    return count
