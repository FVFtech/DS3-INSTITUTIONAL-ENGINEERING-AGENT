from ds3_agent.monitor import REPORT, sync_sources

def test_monitor_writes_report_and_snapshot(tmp_path, monkeypatch):
    import ds3_agent.monitor as m
    monkeypatch.setattr(m, "SNAPSHOT", tmp_path / "snapshot.json")
    monkeypatch.setattr(m, "REPORT", tmp_path / "report.md")
    # Invalid DNS is avoided: patch HTTP client to raise a normal HTTP error.
    import httpx
    class FakeClient:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def head(self, url):
            raise httpx.ConnectError("offline")
    monkeypatch.setattr(m.httpx, "Client", FakeClient)
    result = sync_sources([{"id":"t","title":"T","publisher":"P","url":"https://example.com",
                           "status":"draft","domains":[],"ds3_impact":[],"notes":"n"}])
    assert "t" in result["sources"]
    assert "not proof" in (tmp_path / "report.md").read_text()
