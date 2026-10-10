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
