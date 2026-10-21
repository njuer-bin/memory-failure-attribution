"""Tests for the switchable LLM backend (ollama / openai / anthropic)."""
from __future__ import annotations

import json

from evaluation import llm_api


class _Response:
    def __init__(self, body: dict):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return json.dumps(self._body).encode("utf-8")


def _call(style: str, body: dict, **kwargs):
    captured = {}

    def transport(request, timeout=None):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return _Response(body)

    text = llm_api.completion(
        "hello", "m", base_url="https://example.test", api_key="k",
        style=style, transport=transport, **kwargs,
    )
    return text, captured


def test_ollama_style_keeps_the_legacy_contract():
    text, captured = _call("ollama", {"response": "answer"}, json_mode=True)
    assert text == "answer"
    assert captured["url"] == "https://example.test/api/generate"
    assert captured["payload"]["prompt"] == "hello"
    assert captured["payload"]["format"] == "json"
    assert captured["payload"]["options"] == {"temperature": 0}


def test_openai_style_uses_chat_completions():
    body = {"choices": [{"message": {"content": "answer"}}]}
    text, captured = _call("openai", body, json_mode=True)
    assert text == "answer"
    assert captured["url"] == "https://example.test/chat/completions"
    assert captured["payload"]["messages"] == [{"role": "user", "content": "hello"}]
    assert captured["payload"]["response_format"] == {"type": "json_object"}
    headers = {k.lower(): v for k, v in captured["headers"].items()}
    assert headers["authorization"] == "Bearer k"


def test_anthropic_style_skips_thinking_blocks():
    body = {
        "content": [
            {"type": "thinking", "thinking": "internal"},
            {"type": "text", "text": "answer"},
        ]
    }
    text, captured = _call("anthropic", body)
    assert text == "answer"
    assert captured["url"] == "https://example.test/v1/messages"
    headers = {k.lower(): v for k, v in captured["headers"].items()}
    assert headers["x-api-key"] == "k"
    assert headers["x-opencode-session"]
    assert "authorization" not in headers  # the gateway rejects Bearer auth
    assert captured["payload"]["temperature"] == 0


def test_anthropic_style_raises_on_missing_text_block():
    try:
        _call("anthropic", {"content": [{"type": "thinking", "thinking": "x"}]})
    except RuntimeError as exc:
        assert "empty response" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")


def test_unknown_style_raises():
    try:
        _call("mystery", {})
    except RuntimeError as exc:
        assert "unsupported" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")


def test_empty_response_is_retried_then_succeeds():
    calls = {"n": 0}

    def transport(request, timeout=None):
        calls["n"] += 1
        if calls["n"] == 1:
            return _Response({"content": [{"type": "thinking", "thinking": "x"}]})
        return _Response({"content": [{"type": "text", "text": "ok"}]})

    text = llm_api.completion(
        "hello", "m", base_url="https://example.test", api_key="k",
        style="anthropic", transport=transport,
    )
    assert text == "ok"
    assert calls["n"] == 2
