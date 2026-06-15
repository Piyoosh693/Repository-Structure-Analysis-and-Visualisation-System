"""
API route handlers.

Endpoints:
  POST /api/graph                    — analyze a repo, return nodes + edges
  POST /api/summarize                — get AI summary for a single file
  GET  /api/cache                    — cache statistics
  DELETE /api/cache                  — clear the summary cache
  GET  /api/health                   — liveness check
"""

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from app.api.models import (
    GraphRequest,
    GraphResponse,
    SummarizeRequest,
    SummarizeResponse,
    CacheStatsResponse,
)
from app.core.graph_builder import build_graph
from app.services.ai_service import get_summary_from_disk
from app.services.cache_service import cache_stats, clear_cache
from app.utils.language_map import get_language

router = APIRouter()


# ─── Health check ────────────────────────────────────────────────────────────

@router.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


# ─── Graph analysis ──────────────────────────────────────────────────────────

@router.post("/graph", response_model=GraphResponse, tags=["analysis"])
def get_graph(body: GraphRequest):
    """
    Traverse a local directory, extract dependencies, compute metrics,
    and return a graph of nodes and edges.
    """
    # Expand ~ and environment variables for convenience
    resolved = os.path.expandvars(os.path.expanduser(body.path))

    try:
        graph = build_graph(resolved)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when accessing: {resolved}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

    return graph


# ─── AI summarization ────────────────────────────────────────────────────────

@router.post("/summarize", response_model=SummarizeResponse, tags=["ai"])
def summarize_file(body: SummarizeRequest):
    """
    Generate a plain-English summary of a source file using Gemini.
    Results are cached by content hash — repeated calls on unchanged
    files return instantly without hitting the AI API.
    """
    # Resolve the absolute path to the file
    repo_root = os.path.expandvars(os.path.expanduser(body.repo_root))
    abs_path = str(Path(repo_root) / body.filepath)

    if not Path(abs_path).exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {body.filepath}",
        )

    # Validate language
    # We accept the language passed by the frontend (already computed during graph analysis)
    # but fall back to extension detection as a safety net.
    language = body.language
    if not language:
        ext = Path(abs_path).suffix
        lang_info = get_language(ext)
        language = lang_info["name"] if lang_info else "unknown"

    try:
        result = get_summary_from_disk(
            filepath_abs=abs_path,
            rel_path=body.filepath,
            language=language,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        # Missing API key
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI summarization failed: {e}")

    return result


# ─── Cache management ────────────────────────────────────────────────────────

@router.get("/cache", response_model=CacheStatsResponse, tags=["cache"])
def get_cache_stats():
    """Return statistics about the AI summary cache."""
    return cache_stats()


@router.delete("/cache", tags=["cache"])
def delete_cache():
    """Clear all cached AI summaries."""
    count = clear_cache()
    return {"cleared": count, "message": f"Removed {count} cached summaries."}
