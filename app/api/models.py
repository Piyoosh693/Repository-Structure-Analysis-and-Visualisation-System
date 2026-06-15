"""
Pydantic models for request validation and response serialization.

These match the shapes documented in shared/api-contract.md exactly.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ─── POST /api/graph (Request) ──────────────────────────────────────────────

class GraphRequest(BaseModel):
    path: str = Field(
        ...,
        description="Absolute path to the local repository to analyze",
        examples=["/home/user/myproject"],
    )


# ─── Node & Edge ────────────────────────────────────────────────────────────

class NodeModel(BaseModel):
    id: str = Field(..., description="Relative path from repo root — unique node ID")
    path: str = Field(..., description="Relative path from repo root (same as id, for frontend convenience)")
    label: str = Field(..., description="Filename only, e.g. parser.py")
    language: str = Field(..., description="Detected language, e.g. python")
    loc: int = Field(..., description="Non-blank, non-comment lines of code")
    total_lines: int = Field(..., description="Total raw line count")
    blank_lines: int = Field(..., description="Count of blank lines")
    comment_lines: int = Field(..., description="Count of comment lines")
    complexity: float = Field(..., description="Cyclomatic complexity (avg across functions)")
    size_kb: float = Field(..., description="File size in kilobytes")


class EdgeModel(BaseModel):
    id: str = Field(..., description="Unique edge ID: source->target")
    source: str = Field(..., description="Source node ID (rel_path)")
    target: str = Field(..., description="Target node ID (rel_path)")


class GraphMeta(BaseModel):
    file_count: int
    edge_count: int
    languages: dict[str, int] = Field(default_factory=dict)
    total_loc: int


# ─── GET /api/graph ──────────────────────────────────────────────────────────

class GraphResponse(BaseModel):
    nodes: list[NodeModel]
    edges: list[EdgeModel]
    meta: GraphMeta


# ─── POST /api/summarize ─────────────────────────────────────────────────────

class SummarizeRequest(BaseModel):
    filepath: str = Field(
        ...,
        description="Relative path of the file within the analyzed repo",
        examples=["src/utils/parser.py"],
    )
    repo_root: str = Field(
        ...,
        description="Absolute path to the repo root (so backend can read the file)",
        examples=["/home/user/myproject"],
    )
    language: str = Field(
        ...,
        description="Language string matching the node's language field",
        examples=["python"],
    )
    content_hash: Optional[str] = Field(
        None,
        description="Pre-computed SHA-256 hash. If omitted, backend computes it.",
    )


class SummarizeResponse(BaseModel):
    summary: str
    cached: bool = Field(..., description="True if result came from local cache")
    content_hash: str


# ─── GET /api/cache ──────────────────────────────────────────────────────────

class CacheStatsResponse(BaseModel):
    total_entries: int
    cache_file: str
    size_kb: float


# ─── Error response ──────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
