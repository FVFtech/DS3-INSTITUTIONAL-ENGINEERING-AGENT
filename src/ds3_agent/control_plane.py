"""Durable, fail-closed task and approval control plane. No autonomous execution."""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

VALID_STATES = {"pending", "running", "awaiting_approval", "approved", "rejected", "failed"}
MAX_INPUT = 12000

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

class ControlPlane:
    def __init__(self, path: str | Path):
        self.path = str(path)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY, prompt TEXT NOT NULL, state TEXT NOT NULL,
                    proposal TEXT, error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS approvals (
                    id TEXT PRIMARY KEY, task_id TEXT NOT NULL, reviewer TEXT NOT NULL,
                    decision TEXT NOT NULL, rationale TEXT NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY(task_id) REFERENCES tasks(id)
                );
                CREATE TABLE IF NOT EXISTS audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
                    action TEXT NOT NULL, details TEXT NOT NULL, created_at TEXT NOT NULL
                );
            """)

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _audit(self, db, task_id: str, action: str, details: dict):
        db.execute("INSERT INTO audit(task_id, action, details, created_at) VALUES(?,?,?,?)",
                   (task_id, action, json.dumps(details, sort_keys=True), now()))

    def create(self, prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > MAX_INPUT:
            raise ValueError("Prompt must be nonempty and at most 12000 characters")
        identifier = str(uuid.uuid4())
        timestamp = now()
        with self._connect() as db:
            db.execute("INSERT INTO tasks(id,prompt,state,created_at,updated_at) VALUES(?,?,?,?,?)",
                       (identifier, prompt, "pending", timestamp, timestamp))
            self._audit(db, identifier, "created", {})
        return identifier

    def get(self, task_id: str) -> dict:
        with self._connect() as db:
            row = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if row is None:
            raise KeyError("Task not found")
        result = dict(row)
        if result["proposal"] is not None:
            result["proposal"] = json.loads(result["proposal"])
        return result

    def list(self) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT id,state,created_at,updated_at FROM tasks ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]

    def transition(self, task_id: str, expected: str, state: str, *, proposal=None, error=None):
        allowed = {("pending", "running"), ("running", "awaiting_approval"),
                   ("running", "failed"), ("awaiting_approval", "approved"),
                   ("awaiting_approval", "rejected")}
        if (expected, state) not in allowed:
            raise ValueError("Invalid state transition")
        with self._connect() as db:
            updated = db.execute(
                "UPDATE tasks SET state=?,proposal=COALESCE(?,proposal),error=?,updated_at=? "
                "WHERE id=? AND state=?",
                (state, json.dumps(proposal) if proposal is not None else None,
                 error, now(), task_id, expected))
            if updated.rowcount != 1:
                raise ValueError("Task state changed or task missing")
            self._audit(db, task_id, "transition", {"from": expected, "to": state})

    def decide(self, task_id: str, reviewer: str, decision: str, rationale: str) -> str:
        if decision not in ("approved", "rejected"):
            raise ValueError("Unsupported decision")
        if not reviewer or not reviewer.strip() or reviewer.strip().lower() in {"agent", "llm", "system"}:
            raise ValueError("Human reviewer identity is required")
        if not rationale or not rationale.strip():
            raise ValueError("Rationale is required")
        identifier = str(uuid.uuid4())
        with self._connect() as db:
            updated = db.execute(
                "UPDATE tasks SET state=?,updated_at=? WHERE id=? AND state='awaiting_approval'",
                (decision, now(), task_id))
            if updated.rowcount != 1:
                raise ValueError("Task is not awaiting approval")
            db.execute("INSERT INTO approvals VALUES(?,?,?,?,?,?)",
                       (identifier, task_id, reviewer.strip(), decision, rationale.strip(), now()))
            self._audit(db, task_id, "human_decision",
                        {"reviewer": reviewer.strip(), "decision": decision, "approval_id": identifier})
        return identifier

    def history(self, task_id: str) -> list[dict]:
        self.get(task_id)
        with self._connect() as db:
            rows = db.execute("SELECT action,details,created_at FROM audit WHERE task_id=? ORDER BY id",
                              (task_id,)).fetchall()
        return [{"action": row["action"], "details": json.loads(row["details"]),
                 "created_at": row["created_at"]} for row in rows]
