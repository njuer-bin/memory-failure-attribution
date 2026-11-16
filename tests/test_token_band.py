from experiments.analyze_token_band import band_stats, token_stats


def _row(tokens, memory="学习日语", dimension="intentional", gold="COMMITTED",
         topic=True):
    return {
        "has_legitimate_update": True,
        "dimension": dimension,
        "gold_status": gold,
        "direct_memories": {"5": memory},
        "direct_final_tokens": {"5": tokens},
        "direct_topic_mention": {"5": topic},
    }


def test_token_stats():
    rows = [_row(14), _row(18), _row(20)]
    assert token_stats(rows, "direct") == {"n": 3, "mean": 52 / 3, "min": 14, "max": 20}


def test_band_stats_filters_and_counts_absent():
    rows = [_row(14), _row(16), _row(18), _row(20)]
    stats = band_stats(rows, "direct", 14, 18, True)
    assert stats["n"] == 3
    assert stats["absent"] == 3
    assert stats["rate"] == 1.0
    outside = band_stats(rows, "direct", 14, 18, False)
    assert outside["n"] == 1


def test_band_stats_ignores_stable_rows():
    row = _row(16)
    row["has_legitimate_update"] = False
    assert band_stats([row], "direct", 14, 18, True)["n"] == 0


def test_band_stats_excludes_topic_lost():
    rows = [_row(16, topic=True), _row(16, topic=False)]
    stats = band_stats(rows, "direct", 14, 18, True)
    assert stats["n"] == 1
    assert stats["topic_lost"] == 1
