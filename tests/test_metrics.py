"""
Tests for app.core.metrics
"""

import tempfile
from pathlib import Path
from app.core.traverser import traverse
from app.core.metrics import compute_metrics, _count_lines, _python_complexity


def _make_tree(root: Path, files: dict[str, str]) -> None:
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def _entry_for(tmp: str, filename: str):
    entries = traverse(tmp)
    return next(e for e in entries if e.filename == filename)


# ─── Line counting ───────────────────────────────────────────────────────────

def test_loc_excludes_blank_lines():
    content = "x = 1\n\n\ny = 2\n"
    result = _count_lines(content, "python")
    assert result["blank_lines"] == 2
    assert result["loc"] == 2


def test_loc_excludes_python_comments():
    content = "# this is a comment\nx = 1\n# another\n"
    result = _count_lines(content, "python")
    assert result["comment_lines"] == 2
    assert result["loc"] == 1


def test_loc_excludes_js_comments():
    content = "// comment\nconst x = 1;\n// another\n"
    result = _count_lines(content, "javascript")
    assert result["comment_lines"] == 2
    assert result["loc"] == 1


def test_total_lines_is_all_lines():
    content = "a\nb\n\n# c\nd\n"
    result = _count_lines(content, "python")
    assert result["total_lines"] == 5


def test_empty_file():
    result = _count_lines("", "python")
    assert result["loc"] == 0
    assert result["total_lines"] == 0


# ─── Python complexity ───────────────────────────────────────────────────────

def test_simple_function_complexity():
    code = "def add(a, b):\n    return a + b\n"
    c = _python_complexity(code)
    assert c == 1.0  # no branches → complexity 1


def test_branchy_function_higher_complexity():
    code = (
        "def classify(x):\n"
        "    if x > 10:\n"
        "        return 'high'\n"
        "    elif x > 5:\n"
        "        return 'mid'\n"
        "    else:\n"
        "        return 'low'\n"
    )
    c = _python_complexity(code)
    assert c > 1.0


def test_syntax_error_returns_default():
    c = _python_complexity("def broken(:\n    pass\n")
    assert c == 1.0


# ─── Full compute_metrics ────────────────────────────────────────────────────

def test_compute_metrics_python():
    with tempfile.TemporaryDirectory() as tmp:
        code = (
            "# module docstring\n"
            "\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "\n"
            "def greet(name):\n"
            "    if name:\n"
            "        print(f'Hello {name}')\n"
            "    else:\n"
            "        print('Hello')\n"
        )
        _make_tree(Path(tmp), {"math_utils.py": code})
        entry = _entry_for(tmp, "math_utils.py")
        m = compute_metrics(entry)

        assert m["loc"] > 0
        assert m["total_lines"] == 10
        assert m["comment_lines"] == 1
        assert m["blank_lines"] == 2
        assert m["complexity"] >= 1.0
        assert m["size_kb"] > 0


def test_compute_metrics_js():
    with tempfile.TemporaryDirectory() as tmp:
        code = (
            "// utility functions\n"
            "\n"
            "export function add(a, b) {\n"
            "  return a + b;\n"
            "}\n"
        )
        _make_tree(Path(tmp), {"utils.js": code})
        entry = _entry_for(tmp, "utils.js")
        m = compute_metrics(entry)
        assert m["loc"] > 0
        assert m["complexity"] >= 1.0


def test_loc_is_never_negative():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {"empty.py": ""})
        entry = _entry_for(tmp, "empty.py")
        m = compute_metrics(entry)
        assert m["loc"] >= 0
