"""
Tests for app.core.parser
"""

import tempfile
import pytest
from pathlib import Path

from app.core.traverser import traverse
from app.core.parser import extract_imports, build_edges


def _make_tree(root: Path, files: dict[str, str]) -> None:
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


# ─── Python import extraction ────────────────────────────────────────────────

def test_python_simple_import():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "main.py": "import os\nfrom utils import helper\n",
            "utils.py": "def helper(): pass",
        })
        entries = traverse(tmp)
        entry = next(e for e in entries if e.filename == "main.py")
        raw = extract_imports(entry)
        assert any("utils" in r for r in raw)


def test_python_from_import():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "app/main.py": "from app.models import User\n",
            "app/models.py": "class User: pass",
        })
        entries = traverse(tmp)
        main_entry = next(e for e in entries if e.filename == "main.py")
        raw = extract_imports(main_entry)
        assert any("models" in r for r in raw)


def test_python_edge_resolved():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "main.py": "from utils import helper\n",
            "utils.py": "def helper(): pass\n",
        })
        entries = traverse(tmp)
        edges = build_edges(entries)
        assert ("main.py", "utils.py") in edges


def test_python_stdlib_not_resolved():
    """os, sys, etc. don't exist as files in the repo — should not become edges."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "main.py": "import os\nimport sys\nimport re\n",
        })
        entries = traverse(tmp)
        edges = build_edges(entries)
        assert len(edges) == 0


# ─── JS/TS import extraction ─────────────────────────────────────────────────

def test_js_relative_import_resolved():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "src/App.jsx": "import Button from './components/Button';\n",
            "src/components/Button.jsx": "export default function Button() {}",
        })
        entries = traverse(tmp)
        edges = build_edges(entries)
        assert ("src/App.jsx", "src/components/Button.jsx") in edges


def test_js_third_party_not_resolved():
    """npm packages (no leading dot) should not become edges."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "src/App.jsx": "import React from 'react';\nimport _ from 'lodash';\n",
        })
        entries = traverse(tmp)
        edges = build_edges(entries)
        assert len(edges) == 0


def test_js_import_with_extension():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "index.js": "import helper from './helper.js'",
            "helper.js": "export const x = 1",
        })
        entries = traverse(tmp)
        edges = build_edges(entries)
        assert ("index.js", "helper.js") in edges


# ─── C/C++ includes ──────────────────────────────────────────────────────────

def test_c_local_include_resolved():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "main.c": '#include "utils.h"\nint main() { return 0; }',
            "utils.h": "void helper();",
        })
        entries = traverse(tmp)
        edges = build_edges(entries)
        assert ("main.c", "utils.h") in edges


def test_c_system_include_ignored():
    """<stdio.h> style includes should not become edges."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "main.c": "#include <stdio.h>\nint main() { return 0; }",
        })
        entries = traverse(tmp)
        edges = build_edges(entries)
        assert len(edges) == 0


# ─── Edge deduplication ──────────────────────────────────────────────────────

def test_edges_are_deduplicated():
    """If a file imports the same module twice, only one edge should appear."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "main.py": "from utils import a\nfrom utils import b\n",
            "utils.py": "a = 1\nb = 2\n",
        })
        entries = traverse(tmp)
        edges = build_edges(entries)
        assert edges.count(("main.py", "utils.py")) == 1


# ─── Self-loops ──────────────────────────────────────────────────────────────

def test_no_self_loops():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp), {
            "utils.py": "from utils import something\n",
        })
        entries = traverse(tmp)
        edges = build_edges(entries)
        assert ("utils.py", "utils.py") not in edges
