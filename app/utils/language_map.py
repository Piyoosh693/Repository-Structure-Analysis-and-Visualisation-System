"""
Maps file extensions to language names and import regex patterns.
Each entry has:
  - name: display name shown in the frontend node
  - patterns: list of regex strings that capture import targets
               first capture group must be the imported module/path
"""

LANGUAGE_MAP = {
    # Python
    ".py": {
        "name": "python",
        "patterns": [
            r"^\s*import\s+([\w\.]+)",           # import os.path
            r"^\s*from\s+([\w\.]+)\s+import",    # from utils import x
        ],
    },
    # JavaScript
    ".js": {
        "name": "javascript",
        "patterns": [
            r"from\s+['\"](\./[^'\"]+)['\"]",
            r"from\s+['\"](\.\./[^'\"]+)['\"]",
            r"require\(['\"](\./[^'\"]+)['\"]\)",
            r"require\(['\"](\.\./[^'\"]+)['\"]\)",
        ],
    },
    # TypeScript
    ".ts": {
        "name": "typescript",
        "patterns": [
            r"from\s+['\"](\./[^'\"]+)['\"]",
            r"from\s+['\"](\.\./[^'\"]+)['\"]",
            r"require\(['\"](\./[^'\"]+)['\"]\)",
            r"require\(['\"](\.\./[^'\"]+)['\"]\)",
        ],
    },
    # JSX
    ".jsx": {
        "name": "jsx",
        "patterns": [
            r"from\s+['\"](\./[^'\"]+)['\"]",
            r"from\s+['\"](\.\./[^'\"]+)['\"]",
            r"require\(['\"](\./[^'\"]+)['\"]\)",
            r"require\(['\"](\.\./[^'\"]+)['\"]\)",
        ],
    },
    # TSX
    ".tsx": {
        "name": "tsx",
        "patterns": [
            r"from\s+['\"](\./[^'\"]+)['\"]",
            r"from\s+['\"](\.\./[^'\"]+)['\"]",
            r"require\(['\"](\./[^'\"]+)['\"]\)",
            r"require\(['\"](\.\./[^'\"]+)['\"]\)",
        ],
    },
    # C
    ".c": {
        "name": "c",
        "patterns": [
            r'#include\s+"([^"]+)"',   # local includes only
        ],
    },
    # C++
    ".cpp": {
        "name": "cpp",
        "patterns": [
            r'#include\s+"([^"]+)"',
        ],
    },
    # C/C++ headers
    ".h": {
        "name": "c_header",
        "patterns": [
            r'#include\s+"([^"]+)"',
        ],
    },
    ".hpp": {
        "name": "cpp_header",
        "patterns": [
            r'#include\s+"([^"]+)"',
        ],
    },
    # Java
    ".java": {
        "name": "java",
        "patterns": [
            r"^\s*import\s+([\w\.]+);",
        ],
    },
    # Go
    ".go": {
        "name": "go",
        "patterns": [
            r'"(\.{1,2}/[^"]+)"',
        ],
    },
    # Rust
    ".rs": {
        "name": "rust",
        "patterns": [
            r"(?:use|mod)\s+([\w:]+)",
        ],
    },
}

# Directories to always skip during traversal
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "env", ".env", "dist", "build", "out", ".next", ".nuxt",
    "coverage", ".pytest_cache", ".mypy_cache", ".tox",
    "target",
    "vendor",
    ".idea", ".vscode",
}

# File extensions that are definitely binary / not parseable
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".mp4", ".mp3", ".wav", ".avi", ".mov",
    ".pdf", ".zip", ".tar", ".gz", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".o", ".a",
    ".pyc", ".pyo", ".pyd",
    ".class",
    ".wasm",
    ".lock",
}


def get_language(ext: str) -> dict | None:
    """Return language info for a given extension, or None if unsupported."""
    return LANGUAGE_MAP.get(ext.lower())


def is_supported_extension(ext: str) -> bool:
    return ext.lower() in LANGUAGE_MAP
