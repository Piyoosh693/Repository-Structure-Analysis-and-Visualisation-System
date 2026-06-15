"""
Metrics engine.

Calculates per-file code quality metrics:
  - loc: non-blank, non-comment lines of code
  - complexity: average cyclomatic complexity (Python only via radon;
                approximated for other languages)
  - blank_lines: number of blank lines
  - comment_lines: number of comment/docstring lines
"""

import re
from app.core.traverser import FileEntry


def _count_lines(content: str, language: str) -> dict:
    """
    Count LoC, blank lines, and comment lines for any language.
    Uses simple heuristics — good enough for display metrics.
    """
    lines = content.splitlines()
    total = len(lines)
    blank = 0
    comment = 0

    # Language-specific single-line comment prefixes
    single_comment = {
        "python": "#",
        "javascript": "//",
        "typescript": "//",
        "jsx": "//",
        "tsx": "//",
        "c": "//",
        "cpp": "//",
        "c_header": "//",
        "cpp_header": "//",
        "java": "//",
        "go": "//",
        "rust": "//",
    }
    prefix = single_comment.get(language, "#")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank += 1
        elif stripped.startswith(prefix):
            comment += 1

    loc = total - blank - comment
    return {
        "total_lines": total,
        "loc": max(loc, 0),
        "blank_lines": blank,
        "comment_lines": comment,
    }


def _python_complexity(content: str) -> float:
    """
    Use radon to compute average cyclomatic complexity for Python files.
    Returns a float (average across all functions/methods), or 1.0 on failure.
    """
    try:
        from radon.complexity import cc_visit, average_complexity
        results = cc_visit(content)
        if not results:
            return 1.0
        return round(average_complexity(results), 2)
    except SyntaxError:
        return 1.0
    except Exception:
        return 1.0


def _heuristic_complexity(content: str, language: str) -> float:
    """
    For non-Python languages, estimate complexity by counting
    branch-inducing keywords. This is a rough approximation —
    real cyclomatic complexity requires a full AST.

    Formula: 1 + (number of branch points)
    """
    branch_keywords = {
        "javascript": r"\b(if|else\s+if|for|while|switch|catch|\?\s*:)\b",
        "typescript": r"\b(if|else\s+if|for|while|switch|catch|\?\s*:)\b",
        "jsx":        r"\b(if|else\s+if|for|while|switch|catch|\?\s*:)\b",
        "tsx":        r"\b(if|else\s+if|for|while|switch|catch|\?\s*:)\b",
        "java":       r"\b(if|else\s+if|for|while|switch|catch|\?)\b",
        "c":          r"\b(if|else\s+if|for|while|switch|\?)\b",
        "cpp":        r"\b(if|else\s+if|for|while|switch|\?)\b",
        "c_header":   r"\b(if|else\s+if|for|while|switch|\?)\b",
        "cpp_header": r"\b(if|else\s+if|for|while|switch|\?)\b",
        "go":         r"\b(if|else\s+if|for|switch|select|case)\b",
        "rust":       r"\b(if|else\s+if|for|while|match|loop)\b",
    }
    pattern = branch_keywords.get(language)
    if not pattern:
        return 1.0

    branches = len(re.findall(pattern, content))
    # Normalise — divide by rough "function count" estimated from content size
    lines = max(content.count("\n"), 1)
    # Rough functions per 50 lines
    estimated_functions = max(lines // 50, 1)
    raw = 1 + (branches / estimated_functions)
    return round(min(raw, 50.0), 2)  # cap at 50 for sanity


def compute_metrics(entry: FileEntry) -> dict:
    """
    Compute all metrics for a single FileEntry.
    Returns a dict compatible with the node schema in api-contract.md.
    """
    line_counts = _count_lines(entry.content, entry.language)

    if entry.language == "python":
        complexity = _python_complexity(entry.content)
    else:
        complexity = _heuristic_complexity(entry.content, entry.language)

    return {
        "loc": line_counts["loc"],
        "total_lines": line_counts["total_lines"],
        "blank_lines": line_counts["blank_lines"],
        "comment_lines": line_counts["comment_lines"],
        "complexity": complexity,
        "size_kb": entry.size_kb,
    }
