import json
from pathlib import Path
import pytest
from ds3_agent.registry import load_sources

def test_registry_has_unique_ids_and_https_urls():
    sources = load_sources()
    assert len(sources) >= 8
    assert len({s["id"] for s in sources}) == len(sources)
    assert all(s["url"].startswith("https://") for s in sources)

def test_duplicate_ids_are_rejected(tmp_path: Path):
    p = tmp_path / "sources.json"
    item = {"id":"x","title":"x","publisher":"x","url":"https://example.com",
            "status":"informational","domains":[],"ds3_impact":[],"notes":"x"}
    p.write_text(json.dumps({"sources":[item,item]}), encoding="utf-8")
    with pytest.raises(ValueError, match="unique"):
        load_sources(p)
