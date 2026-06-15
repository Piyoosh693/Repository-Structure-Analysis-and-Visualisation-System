"""
AI service.

Reads a source file, builds a structured prompt, and calls the
Gemini API to generate a short plain-English summary.

Uses the cache layer so each unique file version is only sent once.
"""

import os
from pathlib import Path

import google.generativeai as genai

from app.services.cache_service import (
    compute_hash,
    get_cached_summary,
    set_cached_summary,
)

# Initialise the client once at module load.
# The API key is read from the GEMINI_API_KEY environment variable.
_client_configured = False


def _configure_client() -> None:
    global _client_configured
    if not _client_configured:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set. "
                "Add it to your .env file."
            )
        genai.configure(api_key=api_key)
        _client_configured = True


_SYSTEM_PROMPT = """You are a senior software engineer helping a developer
understand an unfamiliar codebase. You are given the content of a single
source file. Respond with EXACTLY 3 sentences:
  1. What this file's primary purpose is.
  2. The most important function, class, or concept it defines.
  3. How it fits into a typical project (what other parts would depend on it,
     or what it depends on).
Be concrete and specific. Use plain English — no jargon unless unavoidable.
Do not include any preamble, headings, or bullet points. Just the 3 sentences."""

# Maximum characters of file content to send to the AI.
# Beyond this we truncate to control cost and stay within context limits.
_MAX_CONTENT_CHARS = 12_000


def _build_prompt(filepath: str, content: str, language: str) -> str:
    truncated = content[:_MAX_CONTENT_CHARS]
    truncation_note = (
        f"\n\n[File truncated — showing first {_MAX_CONTENT_CHARS} chars of {len(content)} total]"
        if len(content) > _MAX_CONTENT_CHARS
        else ""
    )
    return (
        f"{_SYSTEM_PROMPT}\n\n"
        f"File: {filepath}\n"
        f"Language: {language}\n\n"
        f"```{language}\n{truncated}{truncation_note}\n```"
    )


def get_summary(
    filepath: str,
    content: str,
    language: str,
    content_hash: str | None = None,
) -> dict:
    """
    Return an AI-generated summary for the given file content.

    Args:
        filepath:     Relative path (used in the prompt and cache metadata).
        content:      Full text content of the file.
        language:     Language string (e.g. "python").
        content_hash: Pre-computed SHA-256 hash. Computed here if not provided.

    Returns:
        {
            "summary": str,
            "cached": bool,
            "content_hash": str
        }
    """
    if content_hash is None:
        content_hash = compute_hash(content)

    # Cache hit — return immediately without calling the API
    cached = get_cached_summary(content_hash)
    if cached:
        return {
            "summary": cached,
            "cached": True,
            "content_hash": content_hash,
        }

    # Cache miss — call the AI
    _configure_client()
    prompt = _build_prompt(filepath, content, language)

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    
    summary = response.text.strip()

    # Persist to cache
    set_cached_summary(content_hash, summary, filepath)

    return {
        "summary": summary,
        "cached": False,
        "content_hash": content_hash,
    }


def get_summary_from_disk(filepath_abs: str, rel_path: str, language: str) -> dict:
    """
    Convenience wrapper: reads the file from disk, computes hash, calls get_summary.
    Used by the /api/summarize endpoint when the frontend only sends a filepath.
    """
    path = Path(filepath_abs)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath_abs}")

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise IOError(f"Could not read file: {e}") from e

    content_hash = compute_hash(content)
    return get_summary(rel_path, content, language, content_hash)
