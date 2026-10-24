"""Repository asset paths without changing process cwd or import search path."""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def asset(relative_path: str) -> Path:
    return REPO_ROOT / relative_path
