from experiments.status_drift_judge_calibration import conditions_for
from experiments.status_drift_recursive_pilot import (
    _make_row,
    build_dataset,
    det_condition_status,
    det_match,
    rewrite_matched_budget_schedule,
    select_samples,
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


def test_select_samples_filters_dimensions():
    rows = select_samples(10, "v2", "intentional")
    assert len(rows) == 10
    assert all(r["dimension"] == "intentional" for r in rows)


def test_v3_conditional_states_only_the_condition():
    rows = select_samples(4, "v3", "conditional")
    stable = next(r for r in rows if not r["has_legitimate_update"])
    updated = next(r for r in rows if r["has_legitimate_update"])
    stable_final = stable["turns"][2]["text"]
    updated_final = updated["turns"][2]["text"]
    assert "条件尚未满足" in stable_final
    assert "条件已经满足" in updated_final
    assert "暂时不考虑" not in stable_final
    assert "开始考虑" not in updated_final


def test_v2_conditional_keeps_legacy_action_clause():
    rows = select_samples(2, "v2", "conditional")
    updated = next(r for r in rows if r["has_legitimate_update"])
    assert "开始考虑" in updated["turns"][2]["text"]


def test_det_condition_status_three_states():
    assert det_condition_status("拿不到奖学金，条件不满足") == "ACTIVE"
    assert det_condition_status("没有拿到奖学金") == "ACTIVE"
    assert det_condition_status("无奖学金，未申请研究生") == "ACTIVE"
    assert det_condition_status("已经拿到奖学金了，条件已经满足") == "SATISFIED"
    assert det_condition_status("获得奖学金，条件已满足") == "SATISFIED"
    assert det_condition_status("拿到奖学金，考虑购买电脑。") == "SATISFIED"
    assert det_condition_status("去上海工作。") == "OMITTED"
    assert det_condition_status("条件满足但奖学金未拿到") == "AMBIGUOUS"


def test_rewrite_matched_budget_schedule():
    assert rewrite_matched_budget_schedule(1) == [220]
    assert rewrite_matched_budget_schedule(2) == [220, 180]
    assert rewrite_matched_budget_schedule(3) == [220, 220, 140]
    assert rewrite_matched_budget_schedule(5) == [220, 220, 220, 220, 100]
