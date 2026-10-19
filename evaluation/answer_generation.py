"""Benchmark answer generation and scoring helpers."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from typing import Any

from evaluation.answer_metrics import exact_match, token_f1


BASE_URL = os.getenv("ANSWER_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
ANSWER_API_STYLE = os.getenv("ANSWER_API_STYLE", "ollama").strip().lower()
MODEL = os.getenv("ANSWER_MODEL", "qwen2.5:7b")
TEMPERATURE = float(os.getenv("ANSWER_TEMPERATURE", "0"))
TIMEOUT = float(os.getenv("ANSWER_TIMEOUT_SECONDS", "180"))
F1_THRESHOLD = float(os.getenv("ANSWER_F1_THRESHOLD", "0.5"))


_DATE_PATTERNS = (
    re.compile(r"\b(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?P<month>January|February|March|April|May|June|July|August|September|October|November|December),?\s+(?P<year>\d{4})\b", re.I),
    re.compile(r"\b(?P<month>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?,?\s+(?P<year>\d{4})\b", re.I),
    re.compile(r"\b(?P<year>\d{4})[-/]\s*(?P<month>\d{1,2})[-/]\s*(?P<day>\d{1,2})\b"),
)
_MONTH_YEAR_PATTERN = re.compile(
    r"\b(?P<month>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<year>\d{4})\b",
    re.I,
)


def _normalize(text: str) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _date_from_match(match: re.Match[str]) -> date | None:
    try:
        groups = match.groupdict()
        month = groups["month"]
        if not month.isdigit():
            month = datetime.strptime(month[:3], "%b").month
        day = re.sub(r"(st|nd|rd|th)$", "", groups["day"], flags=re.I)
        return date(int(groups["year"]), int(month), int(day))
    except (TypeError, ValueError):
        return None


def _extract_dates(text: str) -> list[date]:
    """Extract every explicit date in source order, not only the first one."""
    text = str(text or "")
    matches: list[tuple[int, date]] = []
    for pattern in _DATE_PATTERNS:
        for match in pattern.finditer(text):
            parsed = _date_from_match(match)
            if parsed is not None:
                matches.append((match.start(), parsed))
    ordered = [parsed for _, parsed in sorted(matches, key=lambda item: item[0])]
    # Different patterns can match the same date; preserve order while deduplicating.
    return list(dict.fromkeys(ordered))


def _extract_date(text: str) -> date | None:
    dates = _extract_dates(text)
    return dates[0] if dates else None


def _extract_month_period(text: str) -> tuple[date, date] | None:
    """Parse an explicit month/year such as ``June 2023`` as a calendar period."""
    match = _MONTH_YEAR_PATTERN.search(str(text or ""))
    if not match:
        return None
    try:
        month = datetime.strptime(match.group("month")[:3], "%b").month
        year = int(match.group("year"))
        start = date(year, month, 1)
        return start, date(year, month, monthrange(year, month)[1])
    except (TypeError, ValueError):
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


def _temporal_period(text: str, anchor: date | None) -> tuple[date, date] | None:
    """Resolve common benchmark-relative periods against a known anchor date."""
    if anchor is None:
        return None
    normalized = _normalize(text).strip(" .!?;:")

    if normalized == "this week":
        start = anchor - timedelta(days=anchor.weekday())
        return start, start + timedelta(days=6)
    if normalized == "last week":
        start = anchor - timedelta(days=anchor.weekday() + 7)
        return start, start + timedelta(days=6)
    if normalized == "next week":
        start = anchor - timedelta(days=anchor.weekday() - 7)
        return start, start + timedelta(days=6)

    if normalized in {"this month", "last month", "next month"}:
        offset = {"this month": 0, "last month": -1, "next month": 1}[normalized]
        year = anchor.year + (anchor.month - 1 + offset) // 12
        month = (anchor.month - 1 + offset) % 12 + 1
        start = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])
        return start, end

    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6,
    }
    match = re.fullmatch(r"(last|next) (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", normalized)
    if match:
        direction, weekday_name = match.groups()
        target = weekdays[weekday_name]
        delta = (target - anchor.weekday()) % 7
        delta = delta - 7 if direction == "last" else delta + 7
        resolved = anchor + timedelta(days=delta)
        return resolved, resolved

    return None


def _context_anchor_date(context: list[dict[str, Any]]) -> date | None:
    """Find a benchmark/event date from context without inventing one.

    MemoryEngine stores timestamps as Unix milliseconds. Benchmark adapters may
    instead provide human-readable timestamp strings, so accept both forms.
    """
    for item in context:
        for key in ("timestamp", "event_timestamp", "date_time", "datetime"):
            value = item.get(key)
            if isinstance(value, bool) or value is None:
                continue
            if isinstance(value, (int, float)):
                # The memory engine uses milliseconds; also tolerate epoch seconds.
                seconds = float(value) / 1000 if abs(float(value)) >= 100_000_000_000 else float(value)
                try:
                    return datetime.fromtimestamp(seconds, tz=timezone.utc).date()
                except (OverflowError, OSError, ValueError):
                    continue
            anchor = _extract_date(str(value))
            if anchor:
                return anchor
    return None


def _temporal_equivalent(prediction: str, reference: str, anchor: date | None) -> bool:
    """Return True only for explicitly resolvable relative/date pairs."""
    pred_date = _extract_date(prediction)
    ref_date = _extract_date(reference)
    pred_relative = _relative_date(prediction, anchor)
    ref_relative = _relative_date(reference, anchor)
    pred_period = _temporal_period(prediction, anchor)
    ref_period = _temporal_period(reference, anchor)
    pred_month = _extract_month_period(prediction)
    ref_month = _extract_month_period(reference)
    reference_dates = _extract_dates(reference)

    # Benchmark references sometimes contain both a verbal date description and
    # a normalized date (e.g. "the Saturday before 25 May 2023 / May 20, 2023").
    if pred_relative and pred_relative in reference_dates:
        return True

    # Relative weekday answers are resolved by _temporal_period (as a one-day
    # interval), not _relative_date. Compare that resolved day against every
    # explicit date in the reference, including normalized dates after a slash.
    if pred_period and pred_period[0] == pred_period[1] and pred_period[0] in reference_dates:
        return True

    # Some references encode a relative period as an explicit interval, e.g.
    # "the week before 9 June 2023 / From May 29, 2023 to June 4, 2023".
    # Compare that interval with the resolved prediction period rather than the
    # first date in the reference (which may be the anchor date).
    lower_reference = _normalize(reference)
    if pred_period and "from " in lower_reference and " to " in lower_reference:
        range_text = reference[lower_reference.find("from "):]
        range_dates = _extract_dates(range_text)
        if len(range_dates) >= 2 and pred_period == (range_dates[0], range_dates[1]):
            return True

    if pred_date and ref_relative:
        return pred_date == ref_relative
    if ref_date and pred_relative:
        return pred_relative == ref_date
    if pred_date and ref_period:
        return ref_period[0] <= pred_date <= ref_period[1]
    if ref_date and pred_period:
        return pred_period[0] <= ref_date <= pred_period[1]
    if pred_period and ref_period:
        return pred_period == ref_period
    if pred_period and ref_month:
        return pred_period == ref_month
    if ref_period and pred_month:
        return ref_period == pred_month
    return False


def _phrase_match(prediction: str, reference: str) -> bool:
    """Accept a clear reference phrase contained in a fuller direct answer."""
    if not prediction or not reference or prediction == reference:
        return False
    if len(reference.split()) < 2:
        return False
    return reference in prediction


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
    from evaluation.llm_api import completion
    answer = completion(
        _prompt(question, context),
        MODEL,
        base_url=BASE_URL,
        api_key=os.getenv("ANSWER_API_KEY", ""),
        style=ANSWER_API_STYLE,
        timeout=TIMEOUT,
        origin_hint="answer model",
        transport=urllib.request.urlopen,
    )
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
    pred_date = _extract_date(pred)
    ref_date = _extract_date(ref)
    temporal_equivalent = _temporal_equivalent(pred, ref, anchor_date)
    phrase_match = _phrase_match(pred, ref)

    explicit_date_mismatch = bool(pred_date and ref_date and pred_date != ref_date)
    if explicit_date_mismatch:
        correct = False
    else:
        correct = bool(
            em == 1.0
            or f1 >= F1_THRESHOLD
            or temporal_equivalent
            or phrase_match
        )

    return {
        "exact_match": em,
        "token_f1": f1,
        "threshold": F1_THRESHOLD,
        "temporal_equivalent": temporal_equivalent,
        "temporal_anchor_date": anchor_date.isoformat() if anchor_date else None,
        "phrase_match": phrase_match,
        "explicit_date_mismatch": explicit_date_mismatch,
        "correct": correct,
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
