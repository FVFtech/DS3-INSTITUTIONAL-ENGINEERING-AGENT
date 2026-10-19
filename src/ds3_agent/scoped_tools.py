"""Fixed read-only tool registry. Model output never selects arbitrary executables."""
from __future__ import annotations
import json
from pathlib import Path
from .registry import load_sources

MAX_RESULT = 16000
ALLOWED = frozenset({"list_sources", "read_project_file"})
ROOT = Path(__file__).resolve().parents[2]
READABLE = frozenset({"README.md", "docs/architecture/AGENT-ARCHITECTURE.md",
                      "docs/security/THREAT-MODEL.md"})

def invoke(name: str, arguments: dict | None = None) -> str:
    if name not in ALLOWED:
        raise PermissionError("Tool not allowed")
    args = arguments or {}
    if not isinstance(args, dict):
        raise ValueError("Tool arguments must be an object")
    if name == "list_sources":
        if args:
            raise ValueError("list_sources takes no arguments")
        result = json.dumps(load_sources(), sort_keys=True)
    else:
        if set(args) != {"path"} or not isinstance(args["path"], str):
            raise ValueError("read_project_file requires path")
        path = args["path"]
        if path not in READABLE:
            raise PermissionError("Path not allowed")
        result = (ROOT / path).read_text(encoding="utf-8")
    return result[:MAX_RESULT]
