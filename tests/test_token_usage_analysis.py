from experiments.analyze_token_usage import token_ranges


def test_token_ranges_filters_by_tag():
    entries = [
        {"tag": "direct_d5", "eval_count": 10},
        {"tag": "direct_d5", "eval_count": 20},
        {"tag": "recursive_d5", "eval_count": 30},
    ]
    value = token_ranges(entries, "direct_d5")
    assert value == {"calls": 2, "min": 10, "max": 20, "mean": 15.0}


def test_token_ranges_missing_tag():
    assert token_ranges([{"tag": "x", "eval_count": 1}], "direct_d5") is None
