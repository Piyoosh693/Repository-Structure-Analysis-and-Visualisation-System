"""
Tests for app.core.traverser
"""

import os
import tempfile
import pytest
from pathlib import Path

from app.core.traverser import traverse, FileEntry


def _make_tree(root: Path, files: dict[str, str]) -> None:
    """Helper: create a file tree from a dict of {rel_path: content}."""
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


# ─── Basic discovery ─────────────────────────────────────────────────────────

def test_finds_python_files():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "main.py": "import os\nprint('hello')",
            "utils/helper.py": "def add(a, b): return a + b",
        })
        entries = traverse(tmp)
        rel_paths = [e.rel_path for e in entries]
        assert "main.py" in rel_paths
        assert "utils/helper.py" in rel_paths


def test_finds_js_ts_files():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "src/App.jsx": "import React from 'react'",
            "src/index.ts": "export default {}",
        })
        entries = traverse(tmp)
        langs = {e.language for e in entries}
        assert "jsx" in langs
        assert "typescript" in langs


# ─── Filtering ───────────────────────────────────────────────────────────────

def test_skips_node_modules():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "src/App.js": "const x = 1",
            "node_modules/lodash/index.js": "module.exports = {}",
        })
        entries = traverse(tmp)
        rel_paths = [e.rel_path for e in entries]
        assert all("node_modules" not in p for p in rel_paths)


def test_skips_pycache():
    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = Path(tmp) / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "main.cpython-312.pyc").write_bytes(b"\x00\x00fake")
        (Path(tmp) / "main.py").write_text("x = 1")
        entries = traverse(tmp)
        assert all("__pycache__" not in e.rel_path for e in entries)


def test_skips_binary_png():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {"app.py": "x=1"})
        (Path(tmp) / "logo.png").write_bytes(b"\x89PNG\r\n")
        entries = traverse(tmp)
        assert all(e.extension != ".png" for e in entries)


def test_skips_oversized_files():
    with tempfile.TemporaryDirectory() as tmp:
        # Write a >500 KB Python file
        big = Path(tmp) / "big.py"
        big.write_text("x = 1\n" * 100_000)
        entries = traverse(tmp)
        assert all(e.filename != "big.py" for e in entries)


# ─── Error handling ──────────────────────────────────────────────────────────

def test_raises_on_nonexistent_path():
    with pytest.raises(ValueError, match="does not exist"):
        traverse("/this/path/definitely/does/not/exist/abc123")


def test_raises_on_file_not_dir():
    with tempfile.NamedTemporaryFile(suffix=".py") as f:
        with pytest.raises(ValueError, match="not a directory"):
            traverse(f.name)


# ─── Content and metadata ────────────────────────────────────────────────────

def test_entry_has_content():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {"app.py": "print('hi')"})
        entries = traverse(tmp)
        assert entries[0].content == "print('hi')"


def test_entry_has_correct_language():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "a.py": "x=1",
            "b.js": "var x=1",
            "c.cpp": "int main(){}",
        })
        entries = traverse(tmp)
        lang_map = {e.filename: e.language for e in entries}
        assert lang_map["a.py"] == "python"
        assert lang_map["b.js"] == "javascript"
        assert lang_map["c.cpp"] == "cpp"


def test_size_kb_is_positive():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {"mod.py": "x = 1\n" * 100})
        entries = traverse(tmp)
        assert entries[0].size_kb > 0
