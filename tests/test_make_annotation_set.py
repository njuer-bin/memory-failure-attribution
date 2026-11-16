from experiments.make_annotation_set import reliability_items


def _row(i):
    return {
        "sample_id": f"s{i}", "dimension": "epistemic", "proposition": "购买电脑",
        "gold_status": "POSSIBLE", "evidence_turn_ids": [1, 3],
        "dialogue": "dialogue",
        "direct_memories": {"5": "direct memory"},
        "recursive_memories": {"5": "recursive memory"},
        "rewrite_matched_memories": {"5": "matched memory"},
    }


def test_reliability_items_four_conditions():
    items = reliability_items([_row(0)])
    assert [item["condition"] for item in items] == ["raw", "direct", "recursive", "rewrite_matched"]
    assert len(items) == 4
    assert items[0]["depth"] == "raw"
    assert items[1]["depth"] == "5"


def test_reliability_items_thirty_rows():
    items = reliability_items([_row(i) for i in range(30)])
    assert len(items) == 120
