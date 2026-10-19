import pytest
from ds3_agent.control_plane import ControlPlane
from ds3_agent.orchestrator import LLMError, OpenAICompatibleLLM, process_task
from ds3_agent.scoped_tools import invoke

class FakeLLM:
    def propose(self, prompt, context):
        assert prompt and context
        return {"summary": "Proposed improvements", "risks": ["Requires review"],
                "proposed_changes": ["Add a test"], "requested_review": "Human approval"}

def test_model_proposal_is_not_executed(tmp_path):
    db = ControlPlane(tmp_path / "db.sqlite")
    tid = db.create("Propose tests")
    proposal = process_task(db, tid, FakeLLM())
    assert proposal["proposed_changes"] == ["Add a test"]
    assert db.get(tid)["state"] == "awaiting_approval"

def test_failed_model_fails_closed(tmp_path):
    class BadLLM:
        def propose(self, prompt, context):
            return {"unsupported": "output"}
    db = ControlPlane(tmp_path / "db.sqlite")
    tid = db.create("Review tests")
    with pytest.raises(LLMError):
        process_task(db, tid, BadLLM())
    assert db.get(tid)["state"] == "failed"

@pytest.mark.parametrize("name,args", [
    ("shell", {"cmd": "whoami"}), ("read_project_file", {"path": "../secrets"}),
    ("read_project_file", {"path": "config/evolution-policy.json"}),
    ("list_sources", {"unexpected": True})])
def test_tool_scope_denies_unsafe_requests(name, args):
    with pytest.raises((PermissionError, ValueError)):
        invoke(name, args)

def test_llm_rejects_http_and_credentials_in_url():
    with pytest.raises(ValueError):
        OpenAICompatibleLLM(endpoint="http://localhost/chat/completions", api_key="unused")
    with pytest.raises(ValueError):
        OpenAICompatibleLLM(endpoint="https://x:y@example.com/chat/completions", api_key="unused")
