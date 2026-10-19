"""Tests for the deterministic ordering refutation of judge false positives.

The 2026-10-19 audit found 30 judge false positives on two-option ordering
questions ("Which ... first, A or B?"): both qwen2.5:7b and gemma3:12b mark the
wrong pick correct when the evidence resolves the dates. The refutation layer
flips the verdict only when the pick is provably wrong by explicit evidence
dates; everything ambiguous stays with the judge.
"""
from __future__ import annotations

from evaluation.answer_semantic_eval import (
    _earlier_option_by_evidence,
    _item_pair_dates,
    _ordering_pair,
    _ordering_candidate_pick,
    _ordering_refutes_judge,
)

WEBINAR_Q = (
    "Which event did I attend first, the 'Effective Time Management' workshop "
    "or the 'Data Analysis using Python' webinar?"
)
WEBINAR_EVIDENCE = [
    {
        "text": "I've been attending workshops, like the workshop on 'Effective Time Management' at the local community center last Saturday.",
        "timestamp": "2023/05/28 (Sun) 21:04",
    },
    {
        "text": "I participated in a webinar on 'Data Analysis using Python' two months ago.",
        "timestamp": "2023/05/28 (Sun) 07:17",
    },
]


class TestOrderingPair:
    def test_extracts_two_options(self):
        assert _ordering_pair(WEBINAR_Q) == (
            "the 'Effective Time Management' workshop",
            "the 'Data Analysis using Python' webinar",
        )

    def test_no_question_mark(self):
        assert _ordering_pair("Which did I do first, A or B") is None

    def test_non_ordering_question(self):
        assert _ordering_pair("What color is the bike?") is None

    def test_three_way_or_defers(self):
        assert _ordering_pair("Which first, A or B or C?") is None


class TestCandidatePick:
    def test_names_one_option(self):
        options = _ordering_pair(WEBINAR_Q)
        assert _ordering_candidate_pick("The 'Effective Time Management' workshop.", options) == options[0]

    def test_both_named_defers(self):
        options = _ordering_pair(WEBINAR_Q)
        assert _ordering_candidate_pick("Both the workshop and the webinar.", options) is None

    def test_neither_named_defers(self):
        options = _ordering_pair(WEBINAR_Q)
        assert _ordering_candidate_pick("Something else entirely.", options) is None


class TestEarlierByEvidence:
    def test_relative_dates_resolve_order(self):
        earlier = _earlier_option_by_evidence(*_ordering_pair(WEBINAR_Q), WEBINAR_EVIDENCE)
        assert earlier == "the 'Data Analysis using Python' webinar"

    def test_explicit_dates_without_year(self):
        evidence = [
            {"text": "I got a Samsung Galaxy S22 on February 20th.", "timestamp": "2023/03/15 (Wed) 00:56"},
            {"text": "My Dell XPS 13 arrived on February 25th.", "timestamp": "2023/03/15 (Wed) 10:31"},
        ]
        earlier = _earlier_option_by_evidence(
            "the Samsung Galaxy S22", "the Dell XPS 13", evidence
        )
        assert earlier == "the Samsung Galaxy S22"

    def test_same_day_dates_defer(self):
        evidence = [
            {"text": "I washed the bike on Monday.", "timestamp": "2023/03/10 (Fri) 08:11"},
            {"text": "I repaired the car on Monday.", "timestamp": "2023/03/10 (Fri) 08:12"},
        ]
        assert _earlier_option_by_evidence("the bike", "the car", evidence) is None

    def test_unbindable_option_defers(self):
        evidence = [
            {"text": "Something about the workshop without any date.", "timestamp": "2023/05/28 (Sun) 21:04"},
            {"text": "I participated in a webinar on 'Data Analysis using Python' two months ago.", "timestamp": "2023/05/28 (Sun) 07:17"},
        ]
        assert _earlier_option_by_evidence(*_ordering_pair(WEBINAR_Q), evidence) is None


class TestRefutation:
    def test_wrong_pick_is_refuted(self):
        verdict = _ordering_refutes_judge(
            WEBINAR_Q, "The 'Effective Time Management' workshop.", WEBINAR_EVIDENCE
        )
        assert verdict == (
            "the 'Effective Time Management' workshop",
            "the 'Data Analysis using Python' webinar",
        )

    def test_right_pick_is_kept(self):
        assert _ordering_refutes_judge(
            WEBINAR_Q, "The 'Data Analysis using Python' webinar", WEBINAR_EVIDENCE
        ) is None

    def test_ambiguous_candidate_is_kept(self):
        assert _ordering_refutes_judge(
            WEBINAR_Q, "You attended both of these events.", WEBINAR_EVIDENCE
        ) is None

    def test_unresolvable_evidence_keeps_judge(self):
        evidence = [{"text": "No dates here at all, just talk.", "timestamp": None}]
        assert _ordering_refutes_judge(
            WEBINAR_Q, "The 'Effective Time Management' workshop.", evidence
        ) is None
