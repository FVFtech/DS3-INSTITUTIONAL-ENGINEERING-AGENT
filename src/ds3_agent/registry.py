import json
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[2] / "config" / "sources.json"

def load_sources(path: Path = REGISTRY) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = data["sources"]
    ids = [s["id"] for s in sources]
    if len(ids) != len(set(ids)):
        raise ValueError("Source IDs must be unique")
    if any(not s["url"].startswith("https://") for s in sources):
        raise ValueError("Only HTTPS URLs are allowed")
    return sources
