from evaluation.answer_generation import score_answer


def test_timestamp_with_time_and_on_prefix_provides_temporal_anchor():
    result = score_answer(
        "Yesterday.",
        "7 May 2023",
        context=[{"timestamp": "1:56 pm on 8 May, 2023"}],
    )

    assert result["temporal_anchor_date"] == "2023-05-08"
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_simple_timestamp_still_provides_temporal_anchor():
    result = score_answer(
        "Last Saturday.",
        "6 May 2023",
        context=[{"timestamp": "8 May 2023"}],
    )

    assert result["temporal_anchor_date"] == "2023-05-08"
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_last_week_matches_explicit_benchmark_range():
    result = score_answer(
        "Last week.",
        "The week before 9 June 2023 / From May 29, 2023 to June 4, 2023",
        context=[{"timestamp": "7:55 pm on 9 June, 2023"}],
    )
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_last_weekday_matches_explicit_reference_date():
    result = score_answer(
        "Last Tuesday.",
        "The Tuesday before 20 July 2023 / July 18, 2023",
        context=[{"timestamp": "8:56 pm on 20 July, 2023"}],
    )
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_last_weekend_matches_explicit_reference_range():
    result = score_answer(
        "Last weekend.",
        "The weekend before 17 July 2023 / From July 15, 2023 to July 16, 2023",
        context=[{"timestamp": "2:31 pm on 17 July, 2023"}],
    )
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True


def test_two_days_ago_matches_explicit_reference_date():
    result = score_answer(
        "Two days ago.",
        "10 July 2023",
        context=[{"timestamp": "4:33 pm on 12 July, 2023"}],
    )
    assert result["temporal_equivalent"] is True
    assert result["correct"] is True
