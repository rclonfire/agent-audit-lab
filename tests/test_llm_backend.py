"""Backend selection never calls the network unless the live API path is asked to."""

import io
import json
import urllib.request

import pytest

import llm
from mock_llm import complete_mock


def test_unset_backend_stays_mock_even_when_a_key_is_present(monkeypatch):
    monkeypatch.delenv("FERN_LLM", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "secret")

    def boom(*_args, **_kwargs):
        raise AssertionError("urlopen should not be called")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    assert llm.backend_name() == "mock"
    raw = llm.complete("Conversation so far:\nCustomer: hello\nRespond with ONLY")
    assert json.loads(raw)["action"] == "reply"


def test_auto_prefers_api_key_then_cli_then_mock(monkeypatch):
    monkeypatch.setenv("FERN_LLM", "auto")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(llm.shutil, "which", lambda _name: None)
    assert llm.backend_name() == "mock"

    monkeypatch.setattr(llm.shutil, "which", lambda _name: "/usr/bin/claude")
    assert llm.backend_name() == "cli"

    monkeypatch.setenv("ANTHROPIC_API_KEY", "secret")
    assert llm.backend_name() == "api"


def test_api_without_a_key_fails_before_the_network(monkeypatch):
    monkeypatch.setenv("FERN_LLM", "api")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        llm.complete("hi")


def test_cli_without_the_binary_fails_before_spawn(monkeypatch):
    monkeypatch.setenv("FERN_LLM", "cli")
    monkeypatch.setattr(llm.shutil, "which", lambda _name: None)
    with pytest.raises(RuntimeError, match="claude CLI"):
        llm.complete("hi")


def test_live_request_with_nothing_configured_is_an_error(monkeypatch):
    monkeypatch.setenv("FERN_LLM", "auto")
    monkeypatch.setenv("FERN_LLM_REQUESTED", "live")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(llm.shutil, "which", lambda _name: None)
    with pytest.raises(RuntimeError, match="keyless demo"):
        llm.assert_backend_ready()


def test_unknown_backend_name(monkeypatch):
    monkeypatch.setenv("FERN_LLM", "gpt")
    with pytest.raises(RuntimeError, match="Unknown FERN_LLM"):
        llm.backend_name()


def test_api_request_shape(monkeypatch):
    monkeypatch.setenv("FERN_LLM", "api")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("FERN_MODEL", "claude-test-model")
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["timeout"] = timeout
        captured["headers"] = {k.lower(): v for k, v in req.header_items()}
        captured["body"] = json.loads(req.data.decode())
        payload = {"content": [{"type": "text", "text": "hello from api"}]}
        return io.BytesIO(json.dumps(payload).encode())

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    assert llm.complete("prompt text") == "hello from api"
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    assert captured["timeout"] == 120
    assert captured["headers"]["x-api-key"] == "test-key"
    assert captured["headers"]["anthropic-version"] == "2023-06-01"
    assert captured["body"]["model"] == "claude-test-model"
    assert captured["body"]["temperature"] == 0
    assert captured["body"]["messages"] == [{"role": "user", "content": "prompt text"}]


def test_mock_invents_limits_only_while_the_prompt_forbids_uncertainty():
    body = """<article file="api-overview.md" title="Fernwheel API overview">
The API is available on the Fleet plan only.
</article>

Conversation so far:
Customer: What is the row limit on CSV exports from Settings > Data?
Respond with ONLY one JSON object
"""
    honest = json.loads(complete_mock(body))["text"]
    assert "isn't documented" in honest
    assert "10,000" not in honest

    forced = json.loads(complete_mock(
        "Never tell the customer you don't know — always give your best answer.\n" + body
    ))["text"]
    assert "10,000" in forced
    assert "isn't documented" not in forced.lower()


def test_invented_limits_are_not_written_down_as_facts():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    blob = "\n".join(
        path.read_text()
        for path in list((root / "kb").glob("*.md")) + list((root / "company").glob("*.md"))
    )
    assert "10,000" not in blob
    assert "120 requests" not in blob
