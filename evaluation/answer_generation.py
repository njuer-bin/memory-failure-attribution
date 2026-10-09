"""Benchmark answer generation and scoring helpers."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from typing import Any

from evaluation.answer_metrics import exact_match, token_f1


BASE_URL = os.getenv("ANSWER_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL = os.getenv("ANSWER_MODEL", "qwen2.5:7b")
TEMPERATURE = float(os.getenv("ANSWER_TEMPERATURE", "0"))
TIMEOUT = float(os.getenv("ANSWER_TIMEOUT_SECONDS", "180"))
F1_THRESHOLD = float(os.getenv("ANSWER_F1_THRESHOLD", "0.5"))


_DATE_PATTERNS = (
    re.compile(r"\b(?P<day>\d{1,2})\s+(?P<month>January|February|March|April|May|June|July|August|September|October|November|December),?\s+(?P<year>\d{4})\b", re.I),
    re.compile(r"\b(?P<month>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<day>\d{1,2}),?\s+(?P<year>\d{4})\b", re.I),
    re.compile(r"\b(?P<year>\d{4})[-/]\s*(?P<month>\d{1,2})[-/]\s*(?P<day>\d{1,2})\b"),
)


def _normalize(text: str) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _extract_date(text: str) -> date | None:
    text = str(text or "")
    for pattern in _DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        try:
            groups = match.groupdict()
            month = groups["month"]
            if not month.isdigit():
                month = datetime.strptime(month[:3], "%b").month
            return date(int(groups["year"]), int(month), int(groups["day"]))
        except (TypeError, ValueError):
            continue
    return None


def _relative_date(text: str, anchor: date | None) -> date | None:
    if anchor is None:
        return None
    normalized = _normalize(text).strip(" .!?;:")
    offsets = {
        "today": 0,
        "yesterday": -1,
        "tomorrow": 1,
    }
    if normalized in offsets:
        return anchor + timedelta(days=offsets[normalized])
    return None


def _context_anchor_date(context: list[dict[str, Any]]) -> date | None:
    """Find a benchmark/event date from context without inventing one.

    Context timestamps are preferred over arbitrary dates embedded in content.
    This is intentionally conservative: if no parseable timestamp exists, the
    temporal equivalence check is simply not applied.
    """
    for item in context:
        for key in ("timestamp", "event_timestamp", "date_time", "datetime"):
            anchor = _extract_date(str(item.get(key) or ""))
            if anchor:
                return anchor
    return None


def _temporal_equivalent(prediction: str, reference: str, anchor: date | None) -> bool:
    """Return True only for an explicitly resolvable relative/date pair."""
    pred_date = _extract_date(prediction)
    ref_date = _extract_date(reference)
    pred_relative = _relative_date(prediction, anchor)
    ref_relative = _relative_date(reference, anchor)

    if pred_date and ref_relative:
        return pred_date == ref_relative
    if ref_date and pred_relative:
        return pred_relative == ref_date
    return False


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


def score_answer(
    prediction: str,
    reference: str,
    *,
    context: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    pred = _normalize(prediction)
    ref = _normalize(reference)
    em = exact_match(pred, ref)
    f1 = token_f1(pred, ref)
    anchor_date = _context_anchor_date(context or [])
    temporal_equivalent = _temporal_equivalent(pred, ref, anchor_date)
    return {
        "exact_match": em,
        "token_f1": f1,
        "threshold": F1_THRESHOLD,
        "temporal_equivalent": temporal_equivalent,
        "temporal_anchor_date": anchor_date.isoformat() if anchor_date else None,
        "correct": bool(em == 1.0 or f1 >= F1_THRESHOLD or temporal_equivalent),
    }


def generate_and_score(
    question: str,
    reference: str,
    context: list[dict[str, Any]],
) -> dict[str, Any]:
    answer = generate_answer(question, context)
    return {
        "answer": answer,
        **score_answer(answer, reference, context=context),
        "model": MODEL,
        "base_url": BASE_URL,
    }
