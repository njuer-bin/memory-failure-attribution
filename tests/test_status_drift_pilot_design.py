from experiments.status_drift_judge_calibration import conditions_for
from experiments.status_drift_recursive_pilot import (
    _make_row,
    build_dataset,
    det_match,
)


def test_v1_design_preserved():
    rows = build_dataset(6, "v1")
    assert [r["sample_id"] for r in rows] == [
        "epistemic_00", "intentional_00", "conditional_00",
        "epistemic_01", "intentional_01", "conditional_01",
    ]


def test_v2_design_crosses_topic_and_update():
    rows = build_dataset(12, "v2")
    assert len(rows) == 12
    assert sum(r["has_legitimate_update"] for r in rows) == 6
    cells = {(r["dimension"], r["proposition"], r["has_legitimate_update"]) for r in rows}
    assert len(cells) == 12
    dimensions = {r["dimension"] for r in rows}
    topics = {r["proposition"] for r in rows}
    assert dimensions == {"epistemic", "intentional", "conditional"}
    assert len(topics) == 2
    for dimension in dimensions:
        for topic in topics:
            variants = {
                r["has_legitimate_update"] for r in rows
                if r["dimension"] == dimension and r["proposition"] == topic
            }
            assert variants == {False, True}


def test_v2_full_set_is_balanced():
    rows = build_dataset(30, "v2")
    assert len(rows) == 30
    assert sum(r["has_legitimate_update"] for r in rows) == 15
    for dimension in ("epistemic", "intentional", "conditional"):
        assert sum(r["dimension"] == dimension for r in rows) == 10


def test_deterministic_retention_matches_known_strings():
    row = _make_row("epistemic", "购买电脑", True, "x")
    assert det_match("可能购买电脑，但不确定", row)
    assert det_match("买电脑", row)
    assert not det_match("今天天气很好，处理了作业", row)


def test_conditions_use_string_depth_keys():
    row = {
        "dialogue": "full dialogue",
        "direct_memories": {"1": "direct memory"},
        "recursive_memories": {"1": "recursive memory"},
    }
    conditions = dict(conditions_for(row))
    assert conditions["raw"] == "full dialogue"
    assert conditions["direct_d1"] == "direct memory"
    assert conditions["recursive_d1"] == "recursive memory"
    assert conditions["direct_d2"] == ""
