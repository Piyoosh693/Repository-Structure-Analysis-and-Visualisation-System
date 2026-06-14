# API Contract

This document is the single source of truth for all data shapes passed between
the Python backend and the React frontend. **Both team members must agree before
changing anything here.**

---

## Base URL

Development: `http://localhost:8000`

---

## GET /api/graph

Analyze a local repository and return the dependency graph.

### Query Parameters

| Param | Type   | Required | Description                                  |
|-------|--------|----------|----------------------------------------------|
| path  | string | yes      | Absolute path to the repo root on disk       |

### Example Request

```
GET /api/graph?path=/home/user/myproject
```

### Response 200

```json
{
  "nodes": [
    {
      "id": "src/utils/parser.py",
      "label": "parser.py",
      "language": "python",
      "loc": 142,
      "total_lines": 180,
      "blank_lines": 24,
      "comment_lines": 14,
      "complexity": 3.4,
      "size_kb": 4.2
    }
  ],
  "edges": [
    {
      "id": "src/main.py->src/utils/parser.py",
      "source": "src/main.py",
      "target": "src/utils/parser.py"
    }
  ],
  "meta": {
    "file_count": 12,
    "edge_count": 8,
    "languages": { "python": 10, "javascript": 2 },
    "total_loc": 1842
  }
}
```

### Error Responses

| Status | Meaning                                  |
|--------|------------------------------------------|
| 400    | Path does not exist or is not a directory |
| 403    | Permission denied                        |
| 500    | Internal analysis error                  |

---

## POST /api/summarize

Generate a plain-English AI summary for a single file.

### Request Body

```json
{
  "filepath": "src/utils/parser.py",
  "repo_root": "/home/user/myproject",
  "language": "python",
  "content_hash": "abc123def456..."
}
```

`content_hash` is optional. If omitted, the backend computes it.

### Response 200

```json
{
  "summary": "This module handles regex-based dependency extraction for Python, JavaScript, and C files. It defines the build_edges function, which is the primary entry point and resolves raw import strings to actual file paths within the repository. Most other analysis modules call into this one to populate the graph's edge list.",
  "cached": true,
  "content_hash": "abc123def456..."
}
```

### Error Responses

| Status | Meaning                        |
|--------|--------------------------------|
| 404    | File not found at filepath     |
| 503    | AI API key not configured      |
| 500    | AI call failed                 |

---

## GET /api/cache

Returns cache statistics.

```json
{
  "total_entries": 24,
  "cache_file": "/path/to/backend/cache/summaries.json",
  "size_kb": 12.4
}
```

## DELETE /api/cache

Clears all cached summaries.

```json
{ "cleared": 24, "message": "Removed 24 cached summaries." }
```

---

## GET /api/health

Liveness check.

```json
{ "status": "ok" }
```

---

## Node field reference

| Field          | Type   | Description                                        |
|----------------|--------|----------------------------------------------------|
| `id`           | string | Relative path from repo root — used as React Flow node ID |
| `label`        | string | Filename only (no path)                            |
| `language`     | string | `python`, `javascript`, `typescript`, `jsx`, `tsx`, `c`, `cpp`, `java`, `go`, `rust` |
| `loc`          | int    | Non-blank, non-comment lines                       |
| `total_lines`  | int    | Raw line count                                     |
| `blank_lines`  | int    | Blank line count                                   |
| `comment_lines`| int    | Comment/docstring line count                       |
| `complexity`   | float  | Cyclomatic complexity (radon for Python; heuristic for others) |
| `size_kb`      | float  | File size in kilobytes                             |
