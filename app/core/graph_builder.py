"""
Graph builder.

Orchestrates the full pipeline:
  traverser → parser → metrics → structured graph

Output is a dict matching the api-contract.md schema:
  { "nodes": [...], "edges": [...] }
"""

from app.core.traverser import traverse, FileEntry
from app.core.parser import build_edges
from app.core.metrics import compute_metrics


def _make_node(entry: FileEntry, metrics: dict) -> dict:
    """Build a single node object per the API contract."""
    return {
        "id": entry.rel_path,               # unique — relative path from repo root
        "path": entry.rel_path,             # same as id, for frontend convenience
        "label": entry.filename,            # short display name
        "language": entry.language,
        "loc": metrics["loc"],
        "total_lines": metrics["total_lines"],
        "blank_lines": metrics["blank_lines"],
        "comment_lines": metrics["comment_lines"],
        "complexity": metrics["complexity"],
        "size_kb": metrics["size_kb"],
    }


def _make_edge(source: str, target: str) -> dict:
    """Build a single edge object per the API contract."""
    return {
        "id": f"{source}->{target}",
        "source": source,
        "target": target,
    }


def build_graph(root: str) -> dict:
    """
    Full pipeline: traverse → parse → measure → return graph dict.

    Args:
        root: absolute or relative path to the repository root directory.

    Returns:
        { "nodes": list[dict], "edges": list[dict], "meta": dict }

    Raises:
        ValueError: propagated from traverser if root is invalid.
    """
    # 1. Walk the directory
    entries: list[FileEntry] = traverse(root)

    if not entries:
        return {"nodes": [], "edges": [], "meta": {"file_count": 0, "edge_count": 0}}

    # 2. Compute metrics for each file
    nodes = []
    for entry in entries:
        metrics = compute_metrics(entry)
        nodes.append(_make_node(entry, metrics))

    # 3. Resolve dependencies → edges
    raw_edges = build_edges(entries)
    edges = [_make_edge(src, tgt) for src, tgt in raw_edges]

    # 4. Build summary metadata
    meta = {
        "file_count": len(nodes),
        "edge_count": len(edges),
        "languages": _language_summary(entries),
        "total_loc": sum(n["loc"] for n in nodes),
    }

    return {"nodes": nodes, "edges": edges, "meta": meta}


def _language_summary(entries: list[FileEntry]) -> dict:
    """Count files per language for the metadata block."""
    counts: dict[str, int] = {}
    for e in entries:
        counts[e.language] = counts.get(e.language, 0) + 1
    return counts
