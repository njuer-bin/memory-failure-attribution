"""Benchmark answer generation and scoring helpers."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from evaluation.answer_metrics import exact_match, token_f1


BASE_URL = os.getenv("ANSWER_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL = os.getenv("ANSWER_MODEL", "qwen2.5:7b")
TEMPERATURE = float(os.getenv("ANSWER_TEMPERATURE", "0"))
TIMEOUT = float(os.getenv("ANSWER_TIMEOUT_SECONDS", "180"))
F1_THRESHOLD = float(os.getenv("ANSWER_F1_THRESHOLD", "0.5"))


def _normalize(text: str) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _prompt(question: str, context: list[dict[str, Any]]) -> str:
    evidence = chr(10).join(
        "[{}] {}".format(i + 1, str(item.get("content") or "").strip())
        for i, item in enumerate(context)
        if str(item.get("content") or "").strip()
    )
    return (
        "Answer the question using only the evidence below. "
        "Do not invent facts. Give the shortest direct answer possible. "
        "Do not mention the evidence or your reasoning."
        + chr(10) + chr(10)
        + "Question: " + question
        + chr(10) + chr(10)
        + "Evidence:" + chr(10) + evidence
        + chr(10) + chr(10)
        + "Answer:"
    )


def generate_answer(question: str, context: list[dict[str, Any]]) -> str:
    payload = {
        "model": MODEL,
        "prompt": _prompt(question, context),
        "stream": False,
        "options": {"temperature": TEMPERATURE},
    }
    request = urllib.request.Request(
        f"{BASE_URL}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"answer model unavailable at {BASE_URL} (model={MODEL}): {exc}"
        ) from exc
    answer = str(body.get("response") or "").strip()
    if not answer:
        raise RuntimeError("answer model returned an empty response")
    return answer


def score_answer(prediction: str, reference: str) -> dict[str, Any]:
    pred = _normalize(prediction)
    ref = _normalize(reference)
    em = exact_match(pred, ref)
    f1 = token_f1(pred, ref)
    return {
        "exact_match": em,
        "token_f1": f1,
        "threshold": F1_THRESHOLD,
        "correct": bool(em == 1.0 or f1 >= F1_THRESHOLD),
    }


def generate_and_score(
    question: str,
    reference: str,
    context: list[dict[str, Any]],
) -> dict[str, Any]:
    answer = generate_answer(question, context)
    return {
        "answer": answer,
        **score_answer(answer, reference),
        "model": MODEL,
        "base_url": BASE_URL,
    }
