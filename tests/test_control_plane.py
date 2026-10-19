import pytest
from ds3_agent.control_plane import ControlPlane

def test_lifecycle_persists_across_connections(tmp_path):
    path = tmp_path / "tasks.sqlite"
    store = ControlPlane(path)
    task_id = store.create("Review the DS3 audit boundary")
    store.transition(task_id, "pending", "running")
    store.transition(task_id, "running", "awaiting_approval", proposal={"summary": "review"})
    another = ControlPlane(path)
    assert another.get(task_id)["proposal"]["summary"] == "review"
    approval_id = another.decide(task_id, "reviewer@example.org", "approved", "Reviewed offline")
    assert approval_id
    assert store.get(task_id)["state"] == "approved"
    assert [row["action"] for row in store.history(task_id)] == [
        "created", "transition", "transition", "human_decision"]

def test_reject_self_approval_and_invalid_transitions(tmp_path):
    db = ControlPlane(tmp_path / "db.sqlite")
    tid = db.create("Review ledger invariants")
    with pytest.raises(ValueError):
        db.decide(tid, "human", "approved", "not yet")
    db.transition(tid, "pending", "running")
    db.transition(tid, "running", "awaiting_approval", proposal={"summary": "x"})
    with pytest.raises(ValueError):
        db.decide(tid, "agent", "approved", "self approval")
    with pytest.raises(ValueError):
        db.decide(tid, "human", "approved", "")
    db.decide(tid, "human", "rejected", "Insufficient evidence")
    with pytest.raises(ValueError):
        db.decide(tid, "human", "approved", "too late")

def test_input_limits(tmp_path):
    db = ControlPlane(tmp_path / "db.sqlite")
    with pytest.raises(ValueError):
        db.create("")
    with pytest.raises(ValueError):
        db.create("a" * 12001)
