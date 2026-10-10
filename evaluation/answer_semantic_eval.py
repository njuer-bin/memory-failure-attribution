"""Semantic answer evaluation for open-ended long-term QA."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from typing import Any

BASE_URL = os.getenv("ANSWER_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL = os.getenv("SEMANTIC_JUDGE_MODEL", os.getenv("ANSWER_MODEL", "qwen2.5:7b"))
TEMPERATURE = float(os.getenv("SEMANTIC_JUDGE_TEMPERATURE", "0"))
TIMEOUT = float(os.getenv("SEMANTIC_JUDGE_TIMEOUT_SECONDS", "180"))


def _evidence_content(item: Any) -> str:
    """Read evidence text from either trace (`text`) or artifact (`content`) schema."""
    if not isinstance(item, dict):
        return str(item or "").strip()
    return str(item.get("content") or item.get("text") or "").strip()


def _evidence_timestamp(item: Any) -> Any:
    return item.get("timestamp") if isinstance(item, dict) else None


def _joined_evidence(evidence: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in evidence:
        content = _evidence_content(item)
        if not content:
            continue
        timestamp = _evidence_timestamp(item)
        parts.append(f"[{timestamp}] {content}" if timestamp is not None else content)
    return "\n".join(parts)


def _prompt(question: str, candidate: str, evidence: list[dict[str, Any]]) -> str:
    evidence_text = _joined_evidence(evidence)
    return f"""You are an answer-quality evaluator for a research experiment.

The candidate answer below is the benchmark reference answer. Do not assume it is
supported by the evidence. First decide whether the Gold Evidence is sufficient to
answer the exact question and support the reference answer.

Evidence metadata is part of the evidence. Timestamps may resolve relative temporal
expressions such as yesterday, last week, last Saturday, or next month.

Mark evidence_sufficient=false when the evidence describes a different entity/event,
only implies the requested relationship, or cannot establish the requested attribute.
Do not infer that two differently named events are the same.

If evidence_sufficient=true, judge whether the reference answer is correct. Accept
concise and semantically equivalent answers. Use confidence high/medium/low and use
low for genuine ambiguity.

Question:
{question}

Reference answer:
{candidate}

Gold Evidence:
{evidence_text or "[NO EVIDENCE TEXT PROVIDED]"}

Return ONLY JSON:
{{"correct": true, "evidence_sufficient": true, "confidence": "high", "reason": "brief reason"}}
"""


def _call_judge(prompt: str) -> dict[str, Any]:
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": TEMPERATURE},
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            raw = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(
            f"semantic judge unavailable at {BASE_URL} (model={MODEL}): {exc}"
        ) from exc
    try:
        outer = json.loads(raw)
        result = json.loads(outer.get("response", ""))
    except (json.JSONDecodeError, TypeError, AttributeError) as exc:
        raise RuntimeError(f"invalid semantic judge response: {raw[:500]}") from exc
    if not isinstance(result, dict):
        raise RuntimeError("semantic judge response is not a JSON object")
    return result


def _reason_indicates_insufficient_evidence(reason: str) -> bool:
    lowered = reason.lower()
    patterns = (
        "does not provide information", "does not provide any information",
        "no information", "evidence is missing", "no evidence",
        "different event", "different entity", "cannot determine",
        "cannot be determined", "not enough evidence", "insufficient evidence",
    )
    return any(pattern in lowered for pattern in patterns)


def _meaningful_exact_anchor(candidate: str, evidence: list[dict[str, Any]]) -> bool:
    anchor = candidate.strip().lower()
    if not anchor or len(anchor) < 3:
        return False
    return any(anchor in _evidence_content(item).lower() for item in evidence)


def _parse_timestamp(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    match = re.search(r"(\d{1,2})\s+(.+?)\s+on\s+(\d{1,2})\s+([A-Za-z]+),\s+(\d{4})", value)
    if not match:
        return None
    hour = int(match.group(1))
    month_day = match.group(3)
    month_name = match.group(4)
    year = int(match.group(5))
    try:
        return datetime.strptime(f"{month_day} {month_name} {year} {hour}", "%d %B %Y %H")
    except ValueError:
        return None


def _question_dates(question: str) -> set[str]:
    """Extract explicit dates from a question in the benchmark's common formats."""
    dates: set[str] = set()
    for match in re.finditer(r"\b(\d{1,2})\s+([A-Za-z]+),?\s+(\d{4})\b", question):
        try:
            dates.add(datetime.strptime(match.group(0).replace(",", ""), "%d %B %Y").date().isoformat())
        except ValueError:
            pass
    for match in re.finditer(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", question):
        try:
            dates.add(datetime.strptime(match.group(0), "%Y-%m-%d").date().isoformat())
        except ValueError:
            pass
    return dates


def _deterministic_support(question: str, evidence: list[dict[str, Any]]) -> tuple[str, str] | None:
    """Resolve explicit relative-date equivalence; lexical overlap alone is not enough."""
    question_dates = _question_dates(question)
    if not question_dates:
        return None

    for item in evidence:
        content = _evidence_content(item).lower()
        if not content:
            continue
        timestamp = _parse_timestamp(_evidence_timestamp(item))
        if timestamp is None:
            continue

        relative_map = {
            "yesterday": timestamp.date() - timedelta(days=1),
            "last saturday": timestamp.date() - timedelta(days=(timestamp.weekday() - 5) % 7 or 7),
            "last week": timestamp.date() - timedelta(days=7),
            "last sunday": timestamp.date() - timedelta(days=(timestamp.weekday() - 6) % 7 or 7),
        }
        for phrase, target in relative_map.items():
            if phrase in content and target.isoformat() in question_dates:
                return "deterministic_temporal", phrase
    return None


def evaluate_answer(question: str, candidate: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    evidence = list(evidence or [])
    deterministic = _deterministic_support(question, evidence)
    if deterministic is not None:
        return {
            "correct": True,
            "evidence_sufficient": True,
            "confidence": "high",
            "reason": f"Explicit temporal equivalence resolved by evidence timestamp ({deterministic[1]}).",
            "adjudication": deterministic[0],
        }

    result = _call_judge(_prompt(question, candidate, evidence))
    sufficient = bool(result.get("evidence_sufficient"))
    confidence = str(result.get("confidence") or "low").lower()
    reason = str(result.get("reason") or "").strip()
    if sufficient and _reason_indicates_insufficient_evidence(reason):
        sufficient = False
        confidence = "low"
    if sufficient and _meaningful_exact_anchor(candidate, evidence):
        result["correct"] = True
    result["evidence_sufficient"] = sufficient
    result["confidence"] = confidence
    result["reason"] = reason
    result["adjudication"] = "semantic_judge"
    return result
