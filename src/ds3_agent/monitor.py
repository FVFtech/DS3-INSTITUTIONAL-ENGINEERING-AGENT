import json
from datetime import datetime, timezone
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "data" / "source-snapshot.json"
REPORT = ROOT / "docs" / "reports" / "latest-source-report.md"

def sync_sources(sources: list[dict]) -> dict:
    previous = {}
    if SNAPSHOT.exists():
        try:
            previous = json.loads(SNAPSHOT.read_text(encoding="utf-8")).get("sources", {})
        except (OSError, json.JSONDecodeError):
            previous = {}
    current, events = {}, []
    with httpx.Client(timeout=10, follow_redirects=True,
                      headers={"User-Agent": "DS3-Standards-Monitor/0.1"}) as client:
        for source in sources:
            row = {**source, "checked_at": datetime.now(timezone.utc).isoformat(),
                   "http_status": None, "final_url": None, "last_modified": None,
                   "etag": None, "error": None}
            try:
                response = client.head(source["url"])
                if response.status_code in (403, 405, 501):
                    response = client.get(source["url"], headers={"Range": "bytes=0-0"})
                row.update(http_status=response.status_code, final_url=str(response.url),
                           last_modified=response.headers.get("last-modified"),
                           etag=response.headers.get("etag"))
            except httpx.HTTPError as exc:
                row["error"] = type(exc).__name__
            old = previous.get(source["id"])
            if old and any(old.get(k) != row.get(k) for k in
                           ("http_status", "final_url", "last_modified", "etag")):
                events.append({"id": source["id"], "type": "metadata_changed"})
            elif not old and row["http_status"] is not None:
                events.append({"id": source["id"], "type": "first_observation"})
            current[source["id"]] = row
    result = {"generated_at": datetime.now(timezone.utc).isoformat(),
              "warning": "Metadata changes require human verification.",
              "sources": current, "events": events}
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# DS3 Official Source Monitor Report", "",
             f"Generated: {result['generated_at']}", "",
             "> Metadata changes are review signals, not proof of document changes or compliance impact.", "",
             "| ID | Publisher | Source | Status label | HTTP | Last-Modified | Error |",
             "|---|---|---|---|---:|---|---|"]
    for sid, row in current.items():
        lines.append(f"| {sid} | {row['publisher']} | [{row['title']}]({row['url']}) | "
                     f"{row['status']} | {row['http_status'] or '—'} | "
                     f"{row['last_modified'] or '—'} | {row['error'] or '—'} |")
    lines += ["", "## Events requiring review", ""]
    lines += [f"- `{e['id']}`: {e['type']}" for e in events] or ["No metadata changes detected."]
    lines += ["", "## Required human follow-up", "",
              "1. Verify the official document, edition, revision, effective date, and status.",
              "2. Compare document contents/release notes; do not rely only on ETag or Last-Modified.",
              "3. Determine legal and operational applicability with qualified reviewers.",
              "4. Map verified changes to DS3 modules and tests before proposing code changes.", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    return result
