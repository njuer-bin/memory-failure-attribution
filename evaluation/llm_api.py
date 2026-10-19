"""Switchable LLM backend: local Ollama or any OpenAI-compatible chat API.

Selection is env-driven and per component:

- ``ANSWER_API_STYLE`` = ``ollama`` (default) or ``openai``
- ``ANSWER_BASE_URL`` — ollama root, or the OpenAI-compatible root
  (e.g. ``https://api.deepseek.com``); ``/chat/completions`` is appended.
- ``ANSWER_API_KEY`` — required when the style is ``openai``.

The judge additionally honours ``SEMANTIC_JUDGE_API_STYLE`` /
``SEMANTIC_JUDGE_BASE_URL`` / ``SEMANTIC_JUDGE_API_KEY`` so the answer model
and the judge can live on different providers; unset, each falls back to the
answer-side variables, then to ollama.

All completions are temperature-0 research calls; functions here return the
raw response text and never retry, so latency/outage behaviour stays visible
in the experiment logs rather than being silently absorbed.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import uuid
from typing import Any

# Testable transport seam: replace this from tests to stub the network.
_transport = urllib.request.urlopen
# Gateways such as opencode zen require a per-client session id for routing.
_SESSION_ID = str(uuid.uuid4())
# Reasoning-capable models spend part of the budget on a thinking block before
# emitting the answer; 1024 truncates them to an empty text block in practice.
_MAX_TOKENS = int(os.getenv("LLM_API_MAX_TOKENS", "4096"))


def _env_style(prefix: str) -> str:
    style = os.getenv(f"{prefix}_API_STYLE", "").strip().lower()
    return style or "ollama"


def _env_base(prefix: str) -> str:
    default_root = os.getenv("ANSWER_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    return os.getenv(f"{prefix}_BASE_URL", default_root).rstrip("/")


def _env_key(prefix: str) -> str:
    default_key = os.getenv("ANSWER_API_KEY", "")
    return os.getenv(f"{prefix}_API_KEY", default_key)


def completion(
    prompt: str,
    model: str,
    *,
    base_url: str = "",
    api_key: str = "",
    style: str = "ollama",
    timeout: float = 180.0,
    json_mode: bool = False,
    origin_hint: str = "completion",
    transport=None,
) -> str:
    """One completion; returns the assistant text or raises RuntimeError."""
    if transport is None:
        transport = _transport
    if style == "openai":
        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "stream": False,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        url = f"{base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        choice_path = ("choices", 0, "message", "content")
        service = "openai-compatible"
    elif style == "anthropic":
        # Anthropic Messages API (and gateways that accept it), e.g. opencode zen:
        # POST {base}/v1/messages, Bearer auth, content[].text on success.
        url = f"{base_url.rstrip('/')}/v1/messages"
        if "/v1" in url.split("/")[-2] or base_url.rstrip("/").endswith("/v1"):
            url = base_url.rstrip("/") + "/messages"
        payload = {
            "model": model,
            "max_tokens": _MAX_TOKENS,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-opencode-session": os.getenv("LLM_API_SESSION_ID", _SESSION_ID),
        }
        if api_key:
            headers["x-api-key"] = api_key
            headers.setdefault("User-Agent", "llm-api/1.0")
        choice_path = ("content", "text")
        service = "anthropic"
    elif style == "ollama":
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0},
        }
        if json_mode:
            payload["format"] = "json"
        url = f"{base_url}/api/generate"
        headers = {"Content-Type": "application/json"}
        choice_path = ("response",)
        service = "ollama"
    else:
        raise RuntimeError(f"unsupported {origin_hint} API style: {style!r}")

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with transport(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"{service} unavailable at {base_url} (model={model}): {exc}"
        ) from exc

    node: Any = body
    if style == "anthropic":
        blocks = body.get("content")
        if not isinstance(blocks, list):
            raise RuntimeError(
                f"{service} returned an unparseable body for {origin_hint}: "
                f"{json.dumps(body)[:400]}"
            )
        # Reasoning-capable models emit a thinking block before the answer.
        node = next(
            (b.get("text") for b in blocks
             if isinstance(b, dict) and b.get("type") == "text"),
            "",
        )
    else:
        try:
            for key in choice_path:
                node = node[key]
        except (KeyError, IndexError, TypeError):
            raise RuntimeError(
                f"{service} returned an unparseable body for {origin_hint}: "
                f"{json.dumps(body)[:400]}"
            ) from None
    text = str(node or "").strip()
    if not text:
        raise RuntimeError(f"{service} returned an empty response for {origin_hint}")
    return text
