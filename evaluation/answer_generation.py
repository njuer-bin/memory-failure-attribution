"""Benchmark answer generation and scoring helpers."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from calendar import monthrange
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
_MONTH_YEAR_PATTERN = re.compile(
    r"\b(?P<month>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<year>\d{4})\b",
    re.I,
)


def _normalize(text: str) -> str:
    return " ".join(str(text or "").strip().lower().split())


_NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12",
    "once": "1", "twice": "2", "thrice": "3",
}


def _normalize_number_words(text: str) -> str:
    """Map spelled-out numerals to digits so ``Twice`` matches ``2``.

    Trailing/leading punctuation is stripped per token (SQuAD-style) so that
    ``ago.`` and ``ago`` are the same token. Pure lexical normalization; no
    semantic judgment is involved.
    """
    tokens = str(text or "").split()
    cleaned = [t.strip(".,;:!?\"'()[]{}") for t in tokens]
    return " ".join(_NUMBER_WORDS.get(t, t) for t in cleaned if t)


_POLAR_TOKENS = {"yes", "no", "yeah", "nope"}


def _polar_answer_matches(prediction: str, reference: str) -> bool:
    """Accept a bare yes/no answer for a polar question whose reference
    elaborates the justification (e.g. ``Yes, since she collects ...``).

    The elaboration is reasoning support, not part of the answer itself.
    """
    pred = prediction.strip().strip(".,;:!?")
    if pred not in _POLAR_TOKENS:
        return False
    # The reference may hedge the stance ("Likely no; ..."), so look for the
    # first polar token among the first few words of the reference.
    ref_tokens = [t.strip(".,;:!?") for t in reference.strip().split()[:3]]
    ref_stance = next((t for t in ref_tokens if t in _POLAR_TOKENS), None)
    if ref_stance is None:
        return False
    return (pred in {"yes", "yeah"}) == (ref_stance in {"yes", "yeah"})


def _extract_dates(text: str) -> list[date]:
    """Extract all explicit calendar dates from benchmark answers."""
    text = str(text or "")
    dates: list[date] = []
    for pattern in _DATE_PATTERNS:
        for match in pattern.finditer(text):
            try:
                groups = match.groupdict()
                month = groups["month"]
                if not month.isdigit():
                    month = datetime.strptime(month[:3], "%b").month
                parsed = date(int(groups["year"]), int(month), int(groups["day"]))
            except (TypeError, ValueError):
                continue
            if parsed not in dates:
                dates.append(parsed)
    return dates


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
    offsets = {"today": 0, "yesterday": -1, "tomorrow": 1}
    if normalized in offsets:
        return anchor + timedelta(days=offsets[normalized])
    match = re.fullmatch(r"(one|two|three) days? ago", normalized)
    if match:
        count = {"one": 1, "two": 2, "three": 3}[match.group(1)]
        return anchor - timedelta(days=count)
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

    if normalized in {"last weekend", "next weekend"}:
        if normalized == "last weekend":
            saturday = anchor - timedelta(days=(anchor.weekday() - 5) % 7 or 7)
        else:
            saturday = anchor + timedelta(days=(5 - anchor.weekday()) % 7 or 7)
        return saturday, saturday + timedelta(days=1)

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


_BENCHMARK_TIMESTAMP_PATTERN = re.compile(
    r"\b(?:\d{1,2}:\d{2}|\d{1,2})\s*[ap]m\s+on\s+(\d{1,2})\s+"
    r"(January|February|March|April|May|June|July|August|September|October|November|December),?\s+(\d{4})\b",
    flags=re.IGNORECASE,
)


def _parse_benchmark_timestamp(raw: Any) -> date | None:
    """Parse a benchmark conversation timestamp such as ``1:56 pm on 8 May, 2023``.

    These strings come from the benchmark's own session/message metadata (LoCoMo
    ``session_date_time``), not from engine-generated ingestion timestamps.
    """
    raw = str(raw or "").strip()
    if not raw:
        return None
    anchor = _extract_date(raw)
    if anchor:
        return anchor
    match = _BENCHMARK_TIMESTAMP_PATTERN.search(raw)
    if match:
        try:
            month = datetime.strptime(match.group(2)[:3], "%b").month
            return date(int(match.group(3)), month, int(match.group(1)))
        except ValueError:
            return None
    return None


def _context_anchor_date(context: list[dict[str, Any]]) -> date | None:
    """Find a benchmark/event date from context without inventing one."""
    for item in context:
        for key in ("timestamp", "event_timestamp", "date_time", "datetime"):
            anchor = _extract_date(str(item.get(key) or ""))
            if anchor:
                return anchor
            raw = str(item.get(key) or "").strip()
            match = _BENCHMARK_TIMESTAMP_PATTERN.search(raw)
            if match:
                try:
                    month = datetime.strptime(match.group(2)[:3], "%b").month
                    return date(int(match.group(3)), month, int(match.group(1)))
                except ValueError:
                    pass
    return None


def _temporal_equivalent(prediction: str, reference: str, anchor: date | None) -> bool:
    """Return True only for explicitly resolvable relative/date pairs."""
    pred_date = _extract_date(prediction)
    ref_dates = _extract_dates(reference)
    pred_dates = _extract_dates(prediction)
    ref_date = ref_dates[0] if ref_dates else None
    pred_relative = _relative_date(prediction, anchor)
    ref_relative = _relative_date(reference, anchor)
    pred_period = _temporal_period(prediction, anchor)
    ref_period = _temporal_period(reference, anchor)
    pred_month = _extract_month_period(prediction)
    ref_month = _extract_month_period(reference)

    if pred_date and ref_relative:
        return pred_date == ref_relative
    if ref_date and pred_relative:
        # The reference may carry an explicit anchor date in addition to the
        # answer date (e.g. "The friday before 15 July 2023 / July 14, 2023").
        # Compare against every explicit date, not only the first one.
        return any(pred_relative == d for d in ref_dates)
    if pred_relative and any(pred_relative == d for d in ref_dates):
        return True
    if pred_period and len(ref_dates) >= 2:
        ref_range = (min(ref_dates), max(ref_dates))
        if pred_period == ref_range:
            return True
    if pred_period and any(pred_period[0] <= d <= pred_period[1] for d in ref_dates):
        return True
    if pred_dates and ref_period:
        return any(ref_period[0] <= d <= ref_period[1] for d in pred_dates)
    if pred_period and ref_period:
        return pred_period == ref_period
    if pred_period and ref_month:
        return pred_period == ref_month
    if ref_period and pred_month:
        return ref_period == pred_month

    # Some LoCoMo references state the temporal anchor explicitly, e.g.
    # "the weekend before 17 July 2023" or "the Tuesday before 20 July 2023".
    # Real-memory context may carry only an engine-generated numeric timestamp,
    # so using that timestamp as an anchor can be unsafe. When the reference
    # itself explicitly provides the anchor, resolve the candidate against it.
    reference_anchor = None
    before_match = re.search(
        r"\bbefore\s+(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December),?\s+(\d{4})\b",
        reference,
        flags=re.IGNORECASE,
    )
    if before_match:
        try:
            month = datetime.strptime(before_match.group(2)[:3], "%b").month
            reference_anchor = date(int(before_match.group(3)), month, int(before_match.group(1)))
        except ValueError:
            reference_anchor = None
    if reference_anchor is not None:
        pred_relative = _relative_date(prediction, reference_anchor)
        pred_period = _temporal_period(prediction, reference_anchor)
        if pred_relative and any(pred_relative == d for d in ref_dates):
            return True
        if pred_period and any(pred_period[0] <= d <= pred_period[1] for d in ref_dates):
            return True
        if pred_period and len(ref_dates) >= 2:
            return pred_period == (min(ref_dates), max(ref_dates))
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
    evidence_timestamps: list[str] | None = None,
) -> dict[str, Any]:
    pred = _normalize(prediction)
    ref = _normalize(reference)
    pred_norm = _normalize_number_words(pred)
    ref_norm = _normalize_number_words(ref)
    em = exact_match(pred_norm, ref_norm)
    f1 = token_f1(pred_norm, ref_norm)
    anchor_date = _context_anchor_date(context or [])
    anchor_source = "context" if anchor_date else None
    if anchor_date is None:
        # Fallback: the benchmark's own conversation timestamp for the gold
        # evidence (LoCoMo session date_time). This is the same clock the
        # benchmark annotators used to derive absolute-date reference answers,
        # and it is deliberately NOT the engine-generated ingestion timestamp.
        for ts in evidence_timestamps or []:
            anchor_date = _parse_benchmark_timestamp(ts)
            if anchor_date:
                anchor_source = "evidence_timestamp"
                break
    pred_date = _extract_date(pred)
    ref_date = _extract_date(ref)
    temporal_equivalent = _temporal_equivalent(pred, ref, anchor_date)
    phrase_match = _phrase_match(pred, ref)
    polar_match = _polar_answer_matches(pred, ref)

    explicit_date_mismatch = bool(pred_date and ref_date and pred_date != ref_date)
    if explicit_date_mismatch:
        correct = False
    else:
        correct = bool(
            em == 1.0
            or f1 >= F1_THRESHOLD
            or temporal_equivalent
            or phrase_match
            or polar_match
        )

    return {
        "exact_match": em,
        "token_f1": f1,
        "threshold": F1_THRESHOLD,
        "temporal_equivalent": temporal_equivalent,
        "temporal_anchor_date": anchor_date.isoformat() if anchor_date else None,
        "temporal_anchor_source": anchor_source,
        "phrase_match": phrase_match,
        "polar_match": polar_match,
        "explicit_date_mismatch": explicit_date_mismatch,
        "correct": correct,
    }


def generate_and_score(
    question: str,
    reference: str,
    context: list[dict[str, Any]],
    *,
    evidence_timestamps: list[str] | None = None,
) -> dict[str, Any]:
    answer = generate_answer(question, context)
    return {
        "answer": answer,
        **score_answer(answer, reference, context=context, evidence_timestamps=evidence_timestamps),
        "model": MODEL,
        "base_url": BASE_URL,
    }
