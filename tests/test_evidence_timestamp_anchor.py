"""Regression tests for the benchmark-evidence-timestamp temporal anchor.

These cases come from the LoCoMo n=50 attribution validity audit
(experiments/audit_attribution_validity.py): wrong answers whose gold evidence
fully reached the final context, where the prediction is a relative-time
expression that resolves to the reference answer once anchored on the
benchmark conversation timestamp (LoCoMo session date_time).
"""
from evaluation.answer_generation import score_answer


def test_yesterday_resolves_against_evidence_timestamp():
    # conv-26#q0000: evidence "1:56 pm on 8 May, 2023", ref "7 May 2023"
    result = score_answer(
        "Yesterday.",
        "7 May 2023",
        evidence_timestamps=["1:56 pm on 8 May, 2023"],
    )
    assert result["temporal_anchor_date"] == "2023-05-08"
    assert result["temporal_anchor_source"] == "evidence_timestamp"
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_this_month_resolves_to_month_reference():
    # conv-26#q0015: evidence "3 July 2023", ref "July 2023"
    result = score_answer(
        "This month.",
        "July 2023",
        evidence_timestamps=["2:14 pm on 3 July, 2023"],
    )
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_this_week_resolves_to_week_range_reference():
    # conv-26#q0039: ref "The week of 23 August 2023 / From August 21, 2023 to August 27, 2023"
    result = score_answer(
        "This week.",
        "The week of 23 August 2023 / From August 21, 2023 to August 27, 2023",
        evidence_timestamps=["9:41 am on 23 August, 2023"],
    )
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_next_month_resolves_to_following_month():
    # conv-26#q0048: evidence "28 August 2023", ref "September 2023"
    result = score_answer(
        "Next month.",
        "September 2023",
        evidence_timestamps=["3:19 pm on 28 August, 2023"],
    )
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_context_anchor_takes_precedence_over_evidence_timestamp():
    result = score_answer(
        "Yesterday.",
        "7 May 2023",
        context=[{"timestamp": "1:56 pm on 8 May, 2023"}],
        evidence_timestamps=["2:14 pm on 3 July, 2023"],
    )
    assert result["temporal_anchor_date"] == "2023-05-08"
    assert result["temporal_anchor_source"] == "context"
    assert result["correct"] is True


def test_engine_ingestion_epoch_is_not_used_as_anchor():
    # Numeric epoch timestamps (engine ingestion time) must not silently become
    # a temporal anchor; without a benchmark conversation timestamp the
    # relative answer stays unresolved.
    result = score_answer(
        "Yesterday.",
        "7 May 2023",
        context=[{"timestamp": 1792067568534}],
    )
    assert result["temporal_anchor_date"] is None
    assert result["temporal_equivalent"] is False
    assert result["correct"] is False


def test_wrong_relative_answer_stays_incorrect_with_anchor():
    result = score_answer(
        "Yesterday.",
        "2 July 2023",
        evidence_timestamps=["1:56 pm on 8 May, 2023"],
    )
    assert result["temporal_equivalent"] is False
    assert result["correct"] is False


def test_explicit_date_mismatch_still_blocks_correctness():
    result = score_answer(
        "Yesterday.",
        "9 May 2023",
        evidence_timestamps=["1:56 pm on 8 May, 2023"],
    )
    assert result["explicit_date_mismatch"] is False  # prediction carries no explicit date
    assert result["temporal_equivalent"] is False
    assert result["correct"] is False


def test_reference_with_anchor_plus_answer_dates():
    # conv-26#q0022: reference carries an explicit anchor ("before 15 July 2023")
    # AND the answer date ("July 14, 2023"); the evidence timestamp equals the
    # reference anchor. The relative prediction must match the ANSWER date, and
    # must not be rejected by comparing against the anchor date only.
    result = score_answer(
        "Yesterday.",
        "The friday before 15 July 2023 / July 14, 2023",
        evidence_timestamps=["4:02 pm on 15 July, 2023"],
    )
    assert result["temporal_anchor_date"] == "2023-07-15"
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_numeral_word_matches_digit_reference():
    # conv-26#q0030: ref "2", pred "Twice"
    result = score_answer("Twice", "2")
    assert result["exact_match"] == 1.0
    assert result["correct"] is True


def test_spelled_number_matches_digit_reference():
    # conv-26#q0012: ref "10 years ago", pred "Ten years ago."
    result = score_answer("Ten years ago.", "10 years ago")
    assert result["token_f1"] == 1.0
    assert result["correct"] is True


def test_bare_yes_matches_elaborated_polar_reference():
    # conv-26#q0019: ref "Yes, since she collects classic children's books"
    result = score_answer("Yes.", "Yes, since she collects classic children's books")
    assert result["polar_match"] is True
    assert result["correct"] is True


def test_bare_no_matches_elaborated_polar_reference():
    result = score_answer("No.", "LIkely no; though she likes reading, she wants to be a counselor")
    assert result["polar_match"] is True
    assert result["correct"] is True


def test_polar_mismatch_stays_incorrect():
    result = score_answer("No.", "Yes, she is supportive")
    assert result["polar_match"] is False
    assert result["correct"] is False
