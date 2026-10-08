"""Semantic answer evaluation for open-ended long-term QA.

The evaluator separates three questions:
1. Is the supplied Gold Evidence sufficient to answer the question?
2. If it is sufficient, is the candidate answer correct?
3. Is the judge confident enough for attribution?

This is a diagnostic layer, not an absolute ground truth. A conservative lexical-anchor
adjudicator is used only when the judge says the evidence is sufficient and the candidate
contains a meaningful exact phrase from the evidence. This prevents obvious judge
false-negatives such as "Business Administration" and "The Glass Menagerie" from becoming
false F6 reasoning failures.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any


BASE_URL = os.getenv("ANSWER_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL = os.getenv("SEMANTIC_JUDGE_MODEL", os.getenv("ANSWER_MODEL", "qwen2.5:7b"))
TEMPERATURE = float(os.getenv("SEMANTIC_JUDGE_TEMPERATURE", "0"))
TIMEOUT = float(os.getenv("SEMANTIC_JUDGE_TIMEOUT_SECONDS", "180"))
MIN_ANCHOR_TOKENS = int(os.getenv("SEMANTIC_MIN_ANCHOR_TOKENS", "2"))


def _prompt(question: str, candidate: str, evidence: list[dict[str, Any]]) -> str:
    evidence_text = "\n".join(
        f"[{i + 1}] {str(item.get('content') or '').strip()}"
        for i, item in enumerate(evidence)
        if str(item.get("content") or "").strip()
    )
    return f"""You are an answer-quality evaluator for a research experiment.

Evaluate the candidate using ONLY the supplied Gold Evidence.

First decide whether the Gold Evidence is sufficient to answer the exact question.
This is a strict evidence-coverage test, not a plausibility test.

Set "evidence_sufficient" to false when:
- the evidence only mentions a related entity, event, place, or attribute without
  establishing the information requested;
- the question asks about a specific entity/event but the evidence describes a
  different entity/event;
- the evidence contains a phrase that merely implies a relationship, but does not
  explicitly establish that relationship;
- the requested attribute (such as where, when, who, what, or why) cannot be
  determined from the evidence alone.

For example, if the question asks where someone takes yoga classes and the evidence
only says they cannot make it to "Serenity Yoga", that is NOT sufficient evidence
that they take classes there.

Another example: if the question asks when someone volunteered at the local animal
shelter's fundraising dinner, but the evidence only says they volunteered at a
different fundraising dinner called "Love is in the Air" on Valentine's Day, the
evidence is NOT sufficient. Do not infer that the two events are the same.

If evidence_sufficient is true, decide whether the candidate correctly answers the
question. Accept concise answers and semantically equivalent wording. Do not require
the candidate to repeat explanatory text from the evidence.

Set "correct" to false when the candidate answers a different question, contradicts
the evidence, invents unsupported information, or omits necessary information.

Use "confidence" = "high", "medium", or "low". Use low only when the evidence,
question, or candidate is genuinely ambiguous.

Return ONLY valid JSON with exactly these fields:
{{"correct": true, "evidence_sufficient": true, "confidence": "high", "reason": "brief reason"}}

Question:
{question}

Candidate answer:
{candidate}

Gold Evidence:
{evidence_text}
"""


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", text.lower())


def _meaningful_exact_anchor(candidate: str, evidence: list[dict[str, Any]]) -> str | None:
    """Find a conservative exact phrase shared by candidate and evidence.

    This is intentionally narrow: it requires >= MIN_ANCHOR_TOKENS consecutive
    word/character tokens and only operates as an adjudication after the judge
    says the evidence is sufficient.
    """
    candidate_tokens = _tokens(candidate)
    if len(candidate_tokens) < MIN_ANCHOR_TOKENS:
        return None

    for item in evidence:
        content = str(item.get("content") or "")
        evidence_tokens = _tokens(content)
        if len(evidence_tokens) < MIN_ANCHOR_TOKENS:
            continue

        max_len = min(len(candidate_tokens), 12)
        for size in range(max_len, MIN_ANCHOR_TOKENS - 1, -1):
            spans = {
                tuple(candidate_tokens[i : i + size])
                for i in range(len(candidate_tokens) - size + 1)
            }
            for i in range(len(evidence_tokens) - size + 1):
                span = tuple(evidence_tokens[i : i + size])
                if span in spans:
                    phrase = " ".join(span)
                    # Avoid treating generic stop-word-only matches as anchors.
                    if any(
                        len(token) >= 3 or re.search(r"[\u4e00-\u9fff]", token)
                        for token in span
                    ):
                        return phrase
    return None


def _reason_indicates_insufficient_evidence(reason: str) -> bool:
    """Catch cases where the judge's own explanation explicitly describes a mismatch.

    The judge can occasionally emit an internally inconsistent verdict such as
    evidence_sufficient=true while its reason says that the evidence describes a
    different event. This rule is deliberately narrow and only acts on strong
    mismatch language; it does not try to infer sufficiency from generic wording.
    """
    text = reason.strip().lower()
    if not text:
        return False

    strong_patterns = (
        r"only mentions? a different",
        r"mentions? a different (?:event|entity|place|person|thing)",
        r"does not (?:provide|contain|establish) (?:information|evidence)",
        r"not (?:the )?(?:same|requested)",
        r"different (?:event|entity|place|person)",
        r"does not specify the (?:local|specific|requested)",
    )
    return any(re.search(pattern, text) for pattern in strong_patterns)


def evaluate_answer(question: str, candidate: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
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
    if not isinstance(verdict.get("evidence_sufficient"), bool):
        raise RuntimeError(
            f"semantic judge missing boolean 'evidence_sufficient': {raw!r}"
        )

    evidence_sufficient = verdict["evidence_sufficient"]
    judge_correct = verdict["correct"]
    confidence = str(verdict.get("confidence") or "medium").strip().lower()
    if confidence not in {"high", "medium", "low"}:
        confidence = "medium"
    reason = str(verdict.get("reason") or "").strip()

    # Guard against an internally inconsistent judge verdict. If the judge itself
    # explicitly says the evidence is a different event/entity or otherwise lacks
    # the requested information, treat the evidence as insufficient. This prevents
    # such cases from becoming spurious F6 reasoning failures.
    if evidence_sufficient and _reason_indicates_insufficient_evidence(reason):
        evidence_sufficient = False
        judge_correct = False

    final_correct = judge_correct
    adjudication = "judge"

    # Conservative repair for obvious judge false-negatives:
    # only if evidence is sufficient, the judge is confident, and the candidate
    # contains a meaningful exact phrase from the supplied evidence.
    anchor = None
    if evidence_sufficient and not judge_correct and confidence != "low":
        anchor = _meaningful_exact_anchor(candidate, evidence)
        if anchor:
            final_correct = True
            adjudication = "lexical_anchor_override"

    return {
        "correct": final_correct,
        "judge_correct": judge_correct,
        "evidence_sufficient": evidence_sufficient,
        "confidence": confidence,
        "reason": reason,
        "adjudication": adjudication,
        "adjudication_anchor": anchor,
        "model": MODEL,
        "base_url": BASE_URL,
    }
