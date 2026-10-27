from evaluation.answer_generation import score_answer


def test_relative_yesterday_matches_benchmark_date():
    result = score_answer(
        "Yesterday.",
        "7 May 2023",
        context=[{"timestamp": "1:56 pm on 8 May, 2023"}],
    )

    assert result["exact_match"] == 0.0
    assert result["token_f1"] == 0.0
    assert result["temporal_equivalent"] is True
    assert result["temporal_anchor_date"] == "2023-05-08"
    assert result["correct"] is True


def test_different_relative_date_is_not_marked_correct():
    result = score_answer(
        "6 May 2023",
        "7 May 2023",
        context=[{"timestamp": "1:56 pm on 8 May, 2023"}],
    )

    assert result["temporal_equivalent"] is False
    assert result["correct"] is False


def test_relative_date_without_anchor_is_conservative():
    result = score_answer("Yesterday", "7 May 2023")

    assert result["temporal_equivalent"] is False
    assert result["correct"] is False


def test_exact_match_remains_correct():
    result = score_answer("7 May 2023", "7 May 2023")

    assert result["exact_match"] == 1.0
    assert result["correct"] is True


def test_last_week_matches_date_inside_anchor_week():
    result = score_answer(
        "Last week.",
        "5 May 2023",
        context=[{"timestamp": "8 May 2023"}],
    )

    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_last_saturday_matches_reference_date():
    result = score_answer(
        "Last Saturday.",
        "6 May 2023",
        context=[{"timestamp": "8 May 2023"}],
    )

    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_next_month_matches_date_in_next_calendar_month():
    result = score_answer(
        "Next month.",
        "June 2023",
        context=[{"timestamp": "8 May 2023"}],
    )

    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_relative_period_without_anchor_is_conservative():
    result = score_answer("Last week", "5 May 2023")

    assert result["temporal_equivalent"] is False
    assert result["correct"] is False


def test_full_answer_containing_reference_phrase_is_correct():
    result = score_answer(
        "Caroline researched adoption agencies.",
        "adoption agencies",
    )

    assert result["phrase_match"] is True
    assert result["correct"] is True



def test_last_saturday_matches_ordinal_reference_with_epoch_millisecond_anchor():
    from datetime import datetime, timezone

    anchor_ms = int(datetime(2023, 5, 25, 13, 14, tzinfo=timezone.utc).timestamp() * 1000)
    result = score_answer(
        "Last Saturday.",
        "May 20th, 2023",
        context=[{"timestamp": anchor_ms}],
    )

    assert result["temporal_anchor_date"] == "2023-05-25"
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_last_week_matches_ordinal_reference_with_epoch_millisecond_anchor():
    from datetime import datetime, timezone

    anchor_ms = int(datetime(2023, 6, 9, 19, 55, tzinfo=timezone.utc).timestamp() * 1000)
    result = score_answer(
        "Last week.",
        "June 2nd, 2023",
        context=[{"timestamp": anchor_ms}],
    )

    assert result["temporal_anchor_date"] == "2023-06-09"
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_timestamp_anchor_accepts_human_readable_and_epoch_milliseconds():
    from evaluation.answer_generation import _context_anchor_date
    from datetime import date, datetime, timezone

    epoch_ms = int(datetime(2023, 5, 25, tzinfo=timezone.utc).timestamp() * 1000)
    assert _context_anchor_date([{"timestamp": "1:14 pm on 25 May, 2023"}]) == date(2023, 5, 25)
    assert _context_anchor_date([{"timestamp": epoch_ms}]) == date(2023, 5, 25)


def test_last_saturday_matches_normalized_date_in_multi_date_reference():
    from datetime import datetime, timezone

    anchor_ms = int(datetime(2023, 5, 25, 13, 14, tzinfo=timezone.utc).timestamp() * 1000)
    result = score_answer(
        "Last Saturday.",
        "The Saturday before 25 May 2023 / May 20, 2023",
        context=[{"timestamp": anchor_ms}],
    )

    assert result["temporal_anchor_date"] == "2023-05-25"
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_last_week_matches_explicit_date_range_in_reference():
    from datetime import datetime, timezone

    anchor_ms = int(datetime(2023, 6, 9, 19, 55, tzinfo=timezone.utc).timestamp() * 1000)
    result = score_answer(
        "Last week.",
        "The week before 9 June 2023 / From May 29, 2023 to June 4, 2023",
        context=[{"timestamp": anchor_ms}],
    )

    assert result["temporal_anchor_date"] == "2023-06-09"
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True
