"""Semantic answer evaluation for open-ended long-term QA.

The judge evaluates whether a candidate answer correctly answers the question
using the supplied evidence. It intentionally does not require lexical overlap
with a benchmark reference answer, because benchmark references may contain
long explanatory text while the expected answer is a short semantic span.

The judge returns a structured verdict and is only a diagnostic layer; the
existing EM/token-F1 metrics remain available for reproducibility.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


BASE_URL = os.getenv("ANSWER_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL = os.getenv("SEMANTIC_JUDGE_MODEL", os.getenv("ANSWER_MODEL", "qwen2.5:7b"))
TEMPERATURE = float(os.getenv("SEMANTIC_JUDGE_TEMPERATURE", "0"))
TIMEOUT = float(os.getenv("SEMANTIC_JUDGE_TIMEOUT_SECONDS", "180"))


def _prompt(
    question: str,
    candidate: str,
    evidence: list[dict[str, Any]],
) -> str:
    evidence_text = "\n".join(
        f"[{i + 1}] {str(item.get('content') or '').strip()}"
        for i, item in enumerate(evidence)
        if str(item.get("content") or "").strip()
    )
    return f"""You are an answer-quality evaluator for a research experiment.

Determine whether the candidate answer correctly answers the question using
ONLY the evidence. Accept concise answers that are semantically equivalent to
the answer supported by the evidence. Do not require the candidate to repeat
the wording of the evidence. Do not penalize a short answer merely because the
evidence contains additional explanatory text.

Mark correct=false if the candidate answers a different question, contradicts
the evidence, invents unsupported information, or omits information that is
necessary to answer the question.

Return ONLY valid JSON:
{{"correct": true, "reason": "brief reason"}}

Question:
{question}

Candidate answer:
{candidate}

Evidence:
{evidence_text}
"""


def evaluate_answer(
    question: str,
    candidate: str,
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = {
        "model": MODEL,
        "prompt": _prompt(question, candidate, evidence),
        "stream": False,
        "format": "json",
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
            f"semantic judge unavailable at {BASE_URL} (model={MODEL}): {exc}"
        ) from exc

    raw = str(body.get("response") or "").strip()
    if not raw:
        raise RuntimeError("semantic judge returned an empty response")

    try:
        verdict = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"semantic judge returned invalid JSON: {raw!r}") from exc

    if not isinstance(verdict.get("correct"), bool):
        raise RuntimeError(f"semantic judge missing boolean 'correct': {raw!r}")

    return {
        "correct": verdict["correct"],
        "reason": str(verdict.get("reason") or "").strip(),
        "model": MODEL,
        "base_url": BASE_URL,
    }
