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


def test_reference_anchor_resolves_last_weekend_without_context_timestamp():
    result = score_answer(
        "Last weekend.",
        "The weekend before 17 July 2023 / From July 15, 2023 to July 16, 2023",
        context=[{"timestamp": 1791770627945}],
    )

    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_reference_anchor_resolves_last_weekday_without_context_timestamp():
    result = score_answer(
        "Last Tuesday.",
        "The Tuesday before 20 July 2023 / July 18, 2023",
        context=[{"timestamp": 1791770712498}],
    )

    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_full_answer_containing_reference_phrase_is_correct():
    result = score_answer(
        "Caroline researched adoption agencies.",
        "adoption agencies",
    )

    assert result["phrase_match"] is True
    assert result["correct"] is True
