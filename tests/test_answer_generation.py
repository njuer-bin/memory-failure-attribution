from datetime import date

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
