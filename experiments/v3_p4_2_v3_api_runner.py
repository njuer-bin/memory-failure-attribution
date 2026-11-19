"""API-model runner for the V3 P4.2 v3 factorial.

Reuses loading, scoring, and summarization from v3_p4_2_v3_runner, but replaces
the local Ollama /api/chat call with an Anthropic-Messages-API call through an
OpenCode Zen-compatible gateway. Nothing about the prompts, items, or scoring
changes, so results are directly comparable to the qwen/gemma runs.

The gateway needs three headers beyond the standard Anthropic ones:
  x-api-key              the API key
  anthropic-version      2023-06-01
  x-opencode-session     any stable session id (routing hint)

Environment (loaded from ~/.zen_env, never committed):
  ANTHROPIC_AUTH_TOKEN / ZEN_API_KEY   API key
  ANTHROPIC_BASE_URL                    e.g. https://opencode.ai/zen/go
  ZEN_PROXY (default socks5h://127.0.0.1:7892)

Usage (run with the harness sandbox disabled so the SOCKS proxy is reachable):
    set -a; . ~/.zen_env; set +a
    G:/aconda/python.exe -m experiments.v3_p4_2_v3_api_runner \
        --models glm-5.3-flash \
        --base-url "$ANTHROPIC_BASE_URL" \
        --scenario-ids AUT-09 --out-dir results/status_drift_v3_p4_2_v3/api_smoke
"""
from __future__ import annotations

import os
import sys
import time
import uuid

import requests

import experiments.v3_p4_2_v3_runner as R
from experiments.status_drift_recursive_pilot import USAGE_LOG

BASE = os.environ.get("ANTHROPIC_BASE_URL", "").rstrip("/")
KEY = os.environ.get("ZEN_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
PROXY = os.environ.get("ZEN_PROXY", "socks5h://127.0.0.1:7892")
SESSION = os.environ.get("ZEN_SESSION") or ("cc-p42-" + uuid.uuid4().hex)
MAX_TOKENS = int(os.environ.get("ZEN_MAX_TOKENS", "256"))


def api_chat(base_url: str, model: str, messages: list[dict[str, str]],
             timeout: int, retries: int, seed: int | None = None,
             tag: str | None = None, role: str | None = None,
             temperature: float = 0) -> str:
    url = (base_url.rstrip("/") if base_url else BASE) + "/v1/messages"
    headers = {
        "x-api-key": KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
        "x-opencode-session": SESSION,
    }
    payload = {"model": model, "max_tokens": MAX_TOKENS,
               "temperature": temperature, "messages": messages}
    proxies = {"http": PROXY, "https": PROXY} if PROXY else None
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload,
                                 timeout=timeout, proxies=proxies)
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            data = resp.json()
            text = "".join(block.get("text", "") for block in data.get("content", [])
                           if block.get("type") == "text").strip()
            if not text:
                raise ValueError("empty model response")
            usage = data.get("usage", {})
            USAGE_LOG.append({
                "tag": tag, "role": role, "model": model,
                "prompt_eval_count": usage.get("input_tokens"),
                "eval_count": usage.get("output_tokens"),
                "total_duration_ns": None, "load_duration_ns": None,
                "prompt_eval_duration_ns": None, "eval_duration_ns": None,
            })
            return text
        except Exception as exc:  # noqa: BLE001 - optional dependencies can raise anything
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"API request failed: {type(last_error).__name__}: {last_error}")


def api_model_info(base_url: str, model: str) -> dict:
    return {"name": model, "api_base": base_url or BASE, "session": SESSION}


# Patch the runner's module globals so run_model uses the API path.
R.chat = api_chat
R.model_info = api_model_info


if __name__ == "__main__":
    if not KEY:
        raise SystemExit("missing API key (ANTHROPIC_AUTH_TOKEN / ZEN_API_KEY)")
    if not BASE:
        raise SystemExit("missing base URL (ANTHROPIC_BASE_URL)")
    R.main()
