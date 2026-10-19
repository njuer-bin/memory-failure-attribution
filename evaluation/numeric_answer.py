"""Deterministic numeric and duration comparison (audit C5 follow-up).

LongMemEval states its own tolerance in the reference answer:

    "7 days. 8 days (including the last day) is also acceptable."
    "One week. Answers ranging from 7 days to 10 days are also acceptable."

At n=50 the semantic judge could not do that arithmetic reliably and did so
*reproducibly*: it accepted "One month" for "One week", "9 days" for "30 days"
and "32" for "27", while rejecting correct answers in other rows. This module
compares numbers directly against the benchmark's own stated range and returns
``None`` whenever it cannot decide, so the judge keeps every non-numeric answer.
"""
from __future__ import annotations

import re
from typing import Any

# Long answers are not answer-shaped; a number somewhere inside a paragraph is
# not evidence that the paragraph answers a numeric question.
MAX_CANDIDATE_TOKENS = 12

_UNIT_DAYS = {"day": 1, "week": 7, "month": 30, "year": 365}
_WORD_NUMBERS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
}
_WORD = "|".join(_WORD_NUMBERS)
_VALUE = rf"(?:\d+(?:\.\d+)?|{_WORD})"
_UNIT = r"(?:days?|weeks?|months?|years?)"

# A number that is part of a longer token is not a quantity: "S22" is a model
# number, "6:45" and "3/22" are a time and a date, not counts.
_BOUNDARY_LEFT = r"(?<![A-Za-z0-9:/.\-])"
_BOUNDARY_RIGHT = r"(?![A-Za-z0-9:/.\-])"

_QUANTITY = re.compile(
    rf"{_BOUNDARY_LEFT}(?P<value>{_VALUE}){_BOUNDARY_RIGHT}\s*(?P<unit>{_UNIT})?\b"
)
_RANGE = re.compile(
    rf"from\s+(?P<lo>{_VALUE})\s*(?P<u1>{_UNIT})?\s+to\s+(?P<hi>{_VALUE})\s*(?P<u2>{_UNIT})?"
)
# "4 years and 9 months" is one compound duration; canonicalizing each part
# separately would answer a different question, so those defer to the judge.
_COMPOUND = re.compile(rf"{_VALUE}\s*{_UNIT}\s+and\s+{_VALUE}\s*{_UNIT}")


def _number(token: str) -> float | None:
    token = token.strip().lower()
    if token in _WORD_NUMBERS:
        return float(_WORD_NUMBERS[token])
    try:
        return float(token)
    except ValueError:
        return None


def _unit_kind(unit: str | None) -> str | None:
    if not unit:
        return None
    return unit.rstrip("s")


def _quantities(text: str) -> list[tuple[float, str]]:
    """(canonical value, dimension) pairs. Durations are canonicalized to days."""
    found: list[tuple[float, str]] = []
    for match in _QUANTITY.finditer(text):
        value = _number(match.group("value"))
        if value is None:
            continue
        kind = _unit_kind(match.group("unit"))
        if kind in _UNIT_DAYS:
            found.append((value * _UNIT_DAYS[kind], "duration"))
        elif match.group("unit") is None:
            found.append((value, "count"))
    return found


def _question_unit(question: str) -> str | None:
    match = re.search(rf"\b({_UNIT})\b", str(question or "").lower())
    return _unit_kind(match.group(1)) if match else None


def gold_numeric_range(gold_answer: str) -> dict[str, Any] | None:
    """The benchmark's own acceptable values, canonicalized. None if not numeric."""
    text = str(gold_answer or "").lower()
    if _COMPOUND.search(text):
        return None
    quantities = _quantities(text)
    durations = [value for value, dimension in quantities if dimension == "duration"]
    counts = [value for value, dimension in quantities if dimension == "count"]

    if durations:
        allowed = set(durations)
        for match in _RANGE.finditer(text):
            lo, hi = _number(match.group("lo")), _number(match.group("hi"))
            if lo is None or hi is None:
                continue
            kind = _unit_kind(match.group("u1")) or _unit_kind(match.group("u2"))
            factor = _UNIT_DAYS.get(kind or "", 1) if kind else 1
            if not kind:
                # No unit on the range: inherit the unit of the other values.
                factor = _UNIT_DAYS.get(_question_unit(text) or "", 1)
            low, high = sorted((lo * factor, hi * factor))
            if high - low <= 400:
                allowed.update(float(v) for v in range(int(low), int(high) + 1))
        return {"dimension": "duration", "allowed": allowed}
    if counts:
        return {"dimension": "count", "allowed": set(counts)}
    return None


def _candidate_values(candidate: str, question_unit: str | None) -> list[tuple[float, str]]:
    text = str(candidate or "")
    if len(text.split()) > MAX_CANDIDATE_TOKENS:
        return []
    quantities = _quantities(text.lower())
    if question_unit in _UNIT_DAYS:
        factor = _UNIT_DAYS[question_unit]
        # A bare number in a question that asks "how many days" is a day count.
        quantities = [
            (value * factor, "duration") if dimension == "count" else (value, dimension)
            for value, dimension in quantities
        ]
    return quantities


def numeric_verdict(
    gold_answer: str, question: str, candidate: str, *, tolerance: float = 0.5
) -> bool | None:
    """True/False when the benchmark answer states an acceptable numeric range.

    Returns None when the gold answer is not numeric, or when the candidate
    cannot be read as a number of the same dimension, so the judge decides.
    """
    gold = gold_numeric_range(gold_answer)
    if not gold:
        return None
    values = [
        value for value, dimension in _candidate_values(candidate, _question_unit(question))
        if dimension == gold["dimension"]
    ]
    if not values:
        return None
    return any(
        abs(value - allowed) <= tolerance
        for value in values
        for allowed in gold["allowed"]
    )
