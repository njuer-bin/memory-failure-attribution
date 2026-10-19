"""Semantic answer evaluation for open-ended long-term QA.

The evaluator separates evidence sufficiency from answer correctness. The LLM judge
handles ambiguous cases, while deterministic checks protect clear lexical and temporal
cases from judge false-negatives.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from typing import Any

from evaluation.answer_generation import (
    _context_anchor_date,
    _extract_dates,
    _normalize,
    _temporal_period,
    score_answer,
)
from evaluation.numeric_answer import numeric_verdict

BASE_URL = os.getenv("ANSWER_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL = os.getenv("SEMANTIC_JUDGE_MODEL", os.getenv("ANSWER_MODEL", "qwen2.5:7b"))
TEMPERATURE = float(os.getenv("SEMANTIC_JUDGE_TEMPERATURE", "0"))
TIMEOUT = float(os.getenv("SEMANTIC_JUDGE_TIMEOUT_SECONDS", "180"))
MIN_ANCHOR_TOKENS = int(os.getenv("SEMANTIC_MIN_ANCHOR_TOKENS", "2"))
_WORD_AGO = r"(?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)\s+(?:day|week|month|year)s?\s+ago\b"
_RELATIVE_TEMPORAL = re.compile(
    r"\b(?:today|yesterday|tomorrow|this week|last week|next week|"
    r"this month|last month|next month|last|next)\s+"
    r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"
    r"|\b(?:today|yesterday|tomorrow|this week|last week|next week|"
    r"this month|last month|next month)\b"
    r"|\b" + _WORD_AGO,
    re.I,
)


def _evidence_text(evidence: list[dict[str, Any]]) -> str:
    rows: list[str] = []
    for i, item in enumerate(evidence):
        content = str(item.get("content") or item.get("text") or "").strip()
        if not content:
            continue
        metadata: list[str] = []
        for label, key in (("source", "source_id"), ("turn", "turn_id"), ("timestamp", "timestamp")):
            value = item.get(key)
            if value is not None and str(value).strip():
                metadata.append(f"{label}={value}")
        suffix = f" ({', '.join(metadata)})" if metadata else ""
        rows.append(f"[{i + 1}] {content}{suffix}")
    return "\n".join(rows)


def _prompt(question: str, candidate: str, evidence: list[dict[str, Any]], *, candidate_is_reference: bool) -> str:
    if candidate_is_reference:
        candidate_block = f"""The candidate answer below is the benchmark reference answer. Do not assume it is
supported by the evidence. First decide whether the Gold Evidence is sufficient to
answer the exact question and support the reference answer."""
        verdict_line = "If evidence_sufficient=true, judge whether the reference answer is correct."
    else:
        candidate_block = f"""The candidate answer below is a model-generated answer, not the benchmark reference.
First decide whether the Gold Evidence is sufficient to answer the exact question at all;
this decision must not depend on the candidate. Then judge whether the candidate answer
is correct given the question and the Gold Evidence."""
        verdict_line = "If evidence_sufficient=true, judge whether the candidate answer is correct."
    return f"""You are an answer-quality evaluator for a research experiment.

{candidate_block}

Evidence metadata is part of the evidence. Timestamps may resolve relative temporal
expressions such as yesterday, last week, last Saturday, or next month.

Mark evidence_sufficient=false when the evidence describes a different entity/event,
only implies the requested relationship, or cannot establish the requested attribute.
Do not infer that two differently named events are the same.

{verdict_line} Accept concise and semantically equivalent answers. Use confidence
high/medium/low and use low for genuine ambiguity.

Return ONLY JSON:
{{"correct": true, "evidence_sufficient": true, "confidence": "high", "reason": "brief reason"}}

Question:
{question}

Candidate answer:
{candidate}

Gold Evidence:
{_evidence_text(evidence)}
"""


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", text.lower())


def _meaningful_exact_anchor(candidate: str, evidence: list[dict[str, Any]]) -> str | None:
    candidate_tokens = _tokens(candidate)
    if len(candidate_tokens) < MIN_ANCHOR_TOKENS:
        return None
    for item in evidence:
        evidence_tokens = _tokens(str(item.get("content") or item.get("text") or ""))
        if len(evidence_tokens) < MIN_ANCHOR_TOKENS:
            continue
        max_len = min(len(candidate_tokens), 12)
        for size in range(max_len, MIN_ANCHOR_TOKENS - 1, -1):
            spans = {tuple(candidate_tokens[i:i + size]) for i in range(len(candidate_tokens) - size + 1)}
            for i in range(len(evidence_tokens) - size + 1):
                span = tuple(evidence_tokens[i:i + size])
                if span in spans and any(len(t) >= 3 or re.search(r"[\u4e00-\u9fff]", t) for t in span):
                    return " ".join(span)
    return None


_QUESTION_STOPWORDS = {
    "what", "where", "when", "who", "whom", "whose", "which", "why", "how",
    "did", "does", "do", "is", "are", "was", "were", "the", "a", "an", "of",
    "in", "on", "at", "to", "for", "and", "or", "i", "my", "me", "we", "our",
    "it", "that", "this", "there", "have", "has", "had", "before", "after",
    "many", "much", "long", "first", "last", "next", "between", "from",
}


def _question_related(candidate: str, question: str) -> bool:
    """Require an entity-level link between candidate and question.

    Without this, any candidate whose phrase appears in any evidence item is
    short-circuited to correct=True without the question ever being considered.
    """
    q_tokens = {
        t for t in _tokens(question)
        if len(t) >= 3 and t not in _QUESTION_STOPWORDS
    }
    if not q_tokens:
        return False
    return bool(q_tokens & set(_tokens(candidate)))


def _full_coverage_anchor(candidate: str, evidence: list[dict[str, Any]]) -> str | None:
    candidate_tokens = _tokens(candidate)
    if len(candidate_tokens) < MIN_ANCHOR_TOKENS:
        return None
    for item in evidence:
        evidence_tokens = _tokens(str(item.get("content") or item.get("text") or ""))
        n = len(candidate_tokens)
        for i in range(len(evidence_tokens) - n + 1):
            if evidence_tokens[i:i + n] == candidate_tokens:
                return " ".join(candidate_tokens)
    return None


_ORDERING_QUESTION = re.compile(
    r"\bwhich\b.*\b(?:first|earlier)\b|"
    r"\b(?:first|earlier)\b.*\bwhich\b",
    re.I,
)
_ORDERING_TAIL = re.compile(r",\s*(.+?)\s*\?\s*$", re.S)
_RESOLVABLE_RELATIVE = re.compile(
    r"\b" + _WORD_AGO + r"|"
    r"\b(?:last|next)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b|"
    r"\b(?:yesterday|tomorrow|last week|next week|last month|next month)\b",
    re.I,
)


def _ordering_pair(question: str) -> tuple[str, str] | None:
    """The two alternatives of an ordering question ("..., A or B?").

    Requires an ordering question ("Which ... first/earlier") with a two-option
    tail; anything else must stay with the judge. Returns None when either
    option has no content tokens.
    """
    if not _ORDERING_QUESTION.search(question):
        return None
    tail = _ORDERING_TAIL.search(question.strip())
    if not tail:
        return None
    parts = re.split(r"\s+or\s+", tail.group(1), flags=re.I)
    if len(parts) != 2:
        return None
    left, right = (part.strip().strip("'\"") for part in parts)
    if not _tokens(left) or not _tokens(right):
        return None
    return left, right


def _ordering_candidate_pick(candidate: str, options: tuple[str, str]) -> str | None:
    """Which option a candidate names, when exactly one option matches.

    Token-level normalized containment. None if the candidate names both,
    neither, or the evidence is inconclusive — the judge keeps those.
    """
    counts = set(_tokens(candidate))
    matched = [
        option for option in options
        if set(_tokens(option)) - _QUESTION_STOPWORDS <= counts
    ]
    if len(matched) == 1:
        return matched[0]
    return None


def _ordering_refutes_judge(
    question: str, candidate: str, evidence: list[dict[str, Any]]
) -> tuple[str, str] | None:
    """Deterministic false-positive check for two-option ordering questions.

    Every judge false positive observed on 2026-10-19 (30 rows, both judge
    models) named the *wrong* option of the question's own pair, so the pair
    itself is enough: if gold evidence mentions both options and the pick is
    provably wrong by evidence timestamps... it is not provable here. What is
    provable: the option the candidate names must be supported by the evidence
    as the earlier one. This check asserts the contract differently — the pair
    is in the question, the candidate names exactly one option, and the *other*
    option is stated before the picked one by explicit relative dates in the
    evidence. When that cannot be established, the judge is kept.
    """
    pair = _ordering_pair(question)
    if pair is None:
        return None
    pick = _ordering_candidate_pick(candidate, pair)
    if pick is None:
        return None
    other = pair[1] if pick == pair[0] else pair[0]
    earlier = _earlier_option_by_evidence(pair[0], pair[1], evidence)
    if earlier is None:
        return None
    if earlier == pick:
        return None
    return pick, other


def _timestamps_order(before: str, after: str) -> bool | None:
    """True if date_before < date_after, None when either is missing."""
    if not before or not after:
        return None
    try:
        a, b = date.fromisoformat(before), date.fromisoformat(after)
    except ValueError:
        return None
    if a == b:
        return None
    return a < b


_AGO_OFFSET_DAYS = {
    "day": 1, "days": 1, "week": 7, "weeks": 7,
    "month": 30, "months": 30, "year": 365, "years": 365,
}
_AGO_NUMBER_WORDS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12,
}
_AGO_PHRASE = re.compile(
    r"\b(a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)\s+"
    r"(day|week|month|year)s?\s+ago\b",
    re.I,
)


def _ago_phrase_date(normalized: str, stamp):
    match = _AGO_PHRASE.search(normalized)
    if not match or stamp is None:
        return None
    value = match.group(1).lower()
    n = int(value) if value.isdigit() else _AGO_NUMBER_WORDS[value]
    return stamp - timedelta(days=n * _AGO_OFFSET_DAYS[match.group(2).lower()])


def _item_pair_dates(item: dict[str, Any], options: tuple[str, str]) -> dict[str, str]:
    """Date of each option's supporting sentence inside one evidence item.

    A sentence binds an option when the option's content tokens appear in it.
    The date is the first explicit date in the sentence ("March 3rd", with the
    year taken from the turn timestamp when absent); when the sentence carries
    a relative phrase instead, the phrase resolves against the turn timestamp.
    An evidence item whose sentence has no date of its own does not bind the
    option — the turn timestamp alone cannot order same-day turns.
    """
    month_day = re.compile(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?\b",
        re.I,
    )
    content = str(item.get("content") or item.get("text") or "")
    stamp = _timestamp_date(item.get("timestamp"))
    sentences = re.split(r"(?<=[.!?])\s+", content)
    found: dict[str, str] = {}
    for option in options:
        opt_tokens = set(_tokens(option)) - _QUESTION_STOPWORDS
        for sentence in sentences:
            sent_tokens = set(_tokens(sentence))
            if not opt_tokens <= sent_tokens:
                continue
            explicit = _extract_dates(sentence)
            if not explicit:
                match = month_day.search(sentence) if stamp else None
                if match:
                    try:
                        parsed = date(
                            stamp.year,
                            datetime.strptime(match.group(1)[:3], "%b").month,
                            int(match.group(2)),
                        )
                        explicit = [parsed]
                    except ValueError:
                        explicit = []
            if explicit:
                found.setdefault(option, explicit[0].isoformat())
                continue
            for phrase_match in _RELATIVE_TEMPORAL.finditer(sentence):
                normalized = _normalize(phrase_match.group(0)).strip(" .!?;:")
                if not _RESOLVABLE_RELATIVE.search(normalized):
                    continue
                anchor = _ago_phrase_date(normalized, stamp)
                if anchor is None and stamp:
                    period = _temporal_period(normalized, stamp)
                    anchor = period[0] if period else stamp
                if anchor:
                    found.setdefault(option, anchor.isoformat())
    return found


def _timestamp_date(timestamp: Any):
    if timestamp is None:
        return None
    return _context_anchor_date([{"timestamp": timestamp}])


def _earlier_option_by_evidence(
    first: str, second: str, evidence: list[dict[str, Any]]
) -> str | None:
    """The option provably earlier, when evidence dates are unambiguous."""
    dates: dict[str, set] = {}
    for option in (first, second):
        dates[option] = set()
    for item in evidence:
        found = _item_pair_dates(item, (first, second))
        for option, iso in found.items():
            dates[option].add(iso)
    if not all(dates[option] for option in (first, second)):
        return None
    first_day = min(dates[first])
    second_day = min(dates[second])
    result = _timestamps_order(first_day, second_day)
    if result is None:
        return None
    return first if result else second


def _deterministic_support(candidate: str, question: str, evidence: list[dict[str, Any]]) -> tuple[str, str] | None:
    """Return (kind, detail) only for strong evidence-coverage cases.

    Narrowed per the 2026-10-18 audit (C5): the pre-judge deterministic path
    requires the candidate to be fully covered by one evidence item AND to be
    question-related; otherwise the judge decides.
    """
    if _is_temporal_question(question):
        for item in evidence:
            content = str(item.get("content") or item.get("text") or "")
            if not _RELATIVE_TEMPORAL.search(content):
                continue
            context = [{"timestamp": item.get("timestamp")}]
            for match in _RELATIVE_TEMPORAL.finditer(content):
                phrase = match.group(0)
                scored = score_answer(phrase, candidate, context=context)
                if scored.get("temporal_equivalent"):
                    return "deterministic_temporal", phrase

    if _question_related(candidate, question):
        anchor = _full_coverage_anchor(candidate, evidence)
        if anchor:
            return "deterministic_lexical", anchor
    return None


def _looks_like_refusal(candidate: str) -> bool:
    """Reject candidates that decline to answer.

    The post-judge repair exists for concise correct answers, not for model
    refusals: a refusal can still contain an evidence phrase ("a house") and
    must not be converted into a correct answer (audit C5).
    """
    text = candidate.strip().lower()
    patterns = (
        r"\b(?:does not|doesn't|do not|don't|cannot|can't|unable to)\b",
        r"\bno (?:information|evidence|mention)\b",
        r"\bnot (?:provided|mentioned|specified|available|enough|sufficient)\b",
        r"\binsufficient\b",
        r"\bunknown\b",
    )
    return bool(text) and any(re.search(pattern, text) for pattern in patterns)


def _is_temporal_question(question: str) -> bool:
    text = question.lower()
    return bool(re.search(
        r"\bwhen\b|\bwhat (?:day|date|month|year|time)\b|\bhow (?:long|many (?:days|weeks|months|years))\b|\bhow long ago\b",
        text,
    ))


def _is_temporal_answer(candidate: str) -> bool:
    text = candidate.lower()
    return bool(re.search(
        r"\b\d+\s*(?:day|week|month|year|hour|minute)s?\b|\b(?:yesterday|today|tomorrow|last|next)\b",
        text,
    ))


def _repair_is_eligible(candidate: str, question: str) -> bool:
    """Gate the post-judge lexical repair.

    A lexical anchor proves that a phrase occurs in the evidence, not that the
    phrase answers the question. Repair is therefore limited to candidates
    that are question-related, plus temporal answers to temporal questions
    (where the judge repeatedly produced false negatives). Refusals are always
    excluded (audit C5).
    """
    if _looks_like_refusal(candidate):
        return False
    if _question_related(candidate, question):
        return True
    return _is_temporal_question(question) and _is_temporal_answer(candidate)


def _reason_indicates_insufficient_evidence(reason: str) -> bool:
    text = reason.strip().lower()
    patterns = (
        r"only mentions? a different",
        r"mentions? a different (?:event|entity|place|person|thing)",
        r"does not (?:provide|contain|establish) (?:information|evidence)",
        r"not (?:the )?(?:same|requested)",
        r"different (?:event|entity|place|person)",
        r"does not specify the (?:local|specific|requested)",
    )
    return bool(text) and any(re.search(pattern, text) for pattern in patterns)


def numeric_answer_verdict(
    question: str, candidate: str, reference_answer: str
) -> dict[str, Any] | None:
    """Deterministic verdict for numeric/duration answers, or None to defer.

    Exposed so an offline re-scoring pass can apply exactly the same
    short-circuit without re-consulting the judge on every other answer.
    """
    numeric = numeric_verdict(str(reference_answer), question, candidate)
    if numeric is None:
        return None
    return {
        "correct": numeric,
        "judge_correct": None,
        "evidence_sufficient": True,
        "confidence": "high",
        "reason": (
            "Deterministic numeric comparison against the benchmark's own "
            f"acceptable range: {reference_answer!r}."
        ),
        "adjudication": "deterministic_numeric_range",
        "adjudication_anchor": str(reference_answer),
        "model": MODEL,
        "base_url": BASE_URL,
    }


def evaluate_answer(
    question: str,
    candidate: str,
    evidence: list[dict[str, Any]],
    *,
    candidate_is_reference: bool = False,
    reference_answer: str | None = None,
) -> dict[str, Any]:
    if not candidate_is_reference and reference_answer is not None:
        numeric = numeric_answer_verdict(question, candidate, reference_answer)
        if numeric is not None:
            # The benchmark states its own acceptable range for numeric and
            # duration answers; set membership is stricter than both the
            # evidence-coverage check and the judge's arithmetic, so it wins.
            return {**numeric, "candidate_is_reference": candidate_is_reference}

    deterministic = _deterministic_support(candidate, question, evidence)
    if deterministic:
        kind, detail = deterministic
        return {
            "correct": True,
            "judge_correct": True,
            "evidence_sufficient": True,
            "confidence": "high",
            "reason": f"Deterministic evidence-coverage check: {kind}={detail}.",
            "adjudication": kind,
            "adjudication_anchor": detail,
            "model": MODEL,
            "base_url": BASE_URL,
        }

    payload = {
        "model": MODEL,
        "prompt": _prompt(question, candidate, evidence, candidate_is_reference=candidate_is_reference),
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
        raise RuntimeError(f"semantic judge unavailable at {BASE_URL} (model={MODEL}): {exc}") from exc

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
        raise RuntimeError(f"semantic judge missing boolean 'evidence_sufficient': {raw!r}")

    evidence_sufficient = verdict["evidence_sufficient"]
    judge_correct = verdict["correct"]
    confidence = str(verdict.get("confidence") or "medium").strip().lower()
    if confidence not in {"high", "medium", "low"}:
        confidence = "medium"
    reason = str(verdict.get("reason") or "").strip()

    refutation = None
    if judge_correct and evidence_sufficient:
        refutation = _ordering_refutes_judge(question, candidate, evidence)
    if refutation:
        judge_correct = False
        evidence_sufficient = False

    if evidence_sufficient and _reason_indicates_insufficient_evidence(reason):
        evidence_sufficient = False
        judge_correct = False

    final_correct = judge_correct
    adjudication = "judge"
    anchor = None
    if refutation:
        pick, other = refutation
        adjudication = "ordering_refutation"
        anchor = f"{other} precedes {pick}"
    elif (
        evidence_sufficient
        and not judge_correct
        and confidence != "low"
        and _repair_is_eligible(candidate, question)
    ):
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
        "candidate_is_reference": candidate_is_reference,
        "model": MODEL,
        "base_url": BASE_URL,
    }
