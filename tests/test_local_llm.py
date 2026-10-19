import pytest
from ds3_agent.orchestrator import OpenAICompatibleLLM

def test_local_ollama_opt_in(monkeypatch):
    monkeypatch.setenv("DS3_LOCAL_LLM", "1")
    monkeypatch.delenv("DS3_LLM_API_KEY", raising=False)
    monkeypatch.delenv("DS3_LLM_MODEL", raising=False)
    adapter = OpenAICompatibleLLM(endpoint="http://127.0.0.1:11434/v1/chat/completions")
    assert adapter.local is True
    assert adapter.model == "llama3.2:3b"

def test_local_ollama_requires_explicit_opt_in(monkeypatch):
    monkeypatch.delenv("DS3_LOCAL_LLM", raising=False)
    with pytest.raises(ValueError):
        OpenAICompatibleLLM(endpoint="http://localhost:11434/v1/chat/completions")

@pytest.mark.parametrize("endpoint", [
    "http://example.com:11434/v1/chat/completions",
    "http://192.168.1.5:11434/v1/chat/completions",
    "http://127.0.0.1:1234/v1/chat/completions",
    "http://user:pass@localhost:11434/v1/chat/completions",
    "http://localhost:11434/v1/chat/completions?x=1",
])
def test_unsafe_http_endpoints_denied(monkeypatch, endpoint):
    monkeypatch.setenv("DS3_LOCAL_LLM", "1")
    with pytest.raises(ValueError):
        OpenAICompatibleLLM(endpoint=endpoint)

def test_local_no_auth_header(monkeypatch):
    monkeypatch.setenv("DS3_LOCAL_LLM", "1")
    monkeypatch.delenv("DS3_LLM_API_KEY", raising=False)
    adapter = OpenAICompatibleLLM(endpoint="http://127.0.0.1:11434/v1/chat/completions")
    assert adapter.local
