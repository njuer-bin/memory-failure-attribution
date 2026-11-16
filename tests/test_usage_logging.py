from experiments.status_drift_recursive_pilot import summarize_usage


def test_summarize_usage_aggregates_by_tag():
    entries = [
        {"tag": "raw", "prompt_eval_count": 10, "eval_count": 5},
        {"tag": "raw", "prompt_eval_count": 2, "eval_count": 3},
        {"tag": "direct_d5", "prompt_eval_count": 4, "eval_count": 6},
        {"tag": None, "prompt_eval_count": 1, "eval_count": 1},
    ]
    summary = summarize_usage(entries)
    assert summary["raw"] == {"calls": 2, "prompt_tokens": 12, "completion_tokens": 8}
    assert summary["direct_d5"] == {"calls": 1, "prompt_tokens": 4, "completion_tokens": 6}
    assert summary["unknown"]["calls"] == 1


def test_summarize_usage_handles_missing_counts():
    summary = summarize_usage([{"tag": "x", "prompt_eval_count": None, "eval_count": None}])
    assert summary["x"] == {"calls": 1, "prompt_tokens": 0, "completion_tokens": 0}


def test_summarize_usage_separates_roles():
    summary = summarize_usage([
        {"role": "writer", "tag": "direct_d5", "prompt_eval_count": 1, "eval_count": 2},
        {"role": "judge", "tag": "direct_d5", "prompt_eval_count": 3, "eval_count": 4},
    ])
    assert summary["writer:direct_d5"]["completion_tokens"] == 2
    assert summary["judge:direct_d5"]["completion_tokens"] == 4
