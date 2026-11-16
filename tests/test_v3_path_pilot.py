from experiments.v3_path_pilot import (
    HETEROGENEOUS_PATHS,
    normalized_state,
    pairwise_path_rates,
    path_divergence,
)


def _epistemic(gold="CERTAIN"):
    return {"dimension": "epistemic", "gold_status": gold}


def _intentional(gold="COMMITTED"):
    return {"dimension": "intentional", "gold_status": gold}


def _conditional(gold="CONDITION_ACTIVE"):
    return {"dimension": "conditional", "gold_status": gold}


def test_normalized_state_epistemic():
    assert normalized_state(_epistemic(), "用户确认会购买电脑") == "CERTAIN"
    assert normalized_state(_epistemic(), "用户可能购买电脑") == "POSSIBLE"
    assert normalized_state(_epistemic(), "购买电脑，天气变化") == "ABSENT"
    assert normalized_state(_epistemic("POSSIBLE"), "用户确认会购买电脑") == "CERTAIN"


def test_normalized_state_intentional():
    assert normalized_state(_intentional(), "用户决定购买电脑") == "COMMITTED"
    assert normalized_state(_intentional(), "用户考虑购买电脑") == "CONSIDERING"
    assert normalized_state(_intentional(), "购买电脑，天气变化") == "ABSENT"


def test_normalized_state_conditional():
    assert normalized_state(_conditional(), "条件尚未满足") == "ACTIVE"
    assert normalized_state(_conditional(), "条件已经满足") == "SATISFIED"
    assert normalized_state(_conditional(), "购买电脑") == "ABSENT"


def test_path_divergence():
    value = path_divergence(["A", "B", "A"])
    assert value["n"] == 3
    assert abs(value["pairwise_disagreement"] - 2 / 3) < 1e-9
    assert value["distinct"] == 2
    assert abs(value["path_dependence_index"] - 1 / 3) < 1e-9


def test_path_divergence_single_path():
    value = path_divergence(["A"])
    assert value["pairwise_disagreement"] is None


def test_heterogeneous_paths_are_five_unique_specs():
    assert len(HETEROGENEOUS_PATHS) == 5
    assert set(HETEROGENEOUS_PATHS) == {"S1", "S2", "PEEK", "PARA", "TEMP"}
    assert len({str(spec) for spec in HETEROGENEOUS_PATHS.values()}) == 5


def test_pairwise_path_rates():
    records = [
        {"paths": {"A": {"topic_mentioned": True, "final_state": "X"},
                   "B": {"topic_mentioned": True, "final_state": "Y"}}},
        {"paths": {"A": {"topic_mentioned": True, "final_state": "X"},
                   "B": {"topic_mentioned": True, "final_state": "X"}}},
    ]
    rates = pairwise_path_rates(records, ["A", "B"])
    assert rates["A_B"] == {"n": 2, "disagree": 1, "rate": 0.5}


def test_neutral_paraphrase_prompt_differs():
    from experiments.status_drift_recursive_pilot import writer_prompt
    assert writer_prompt("x", 100, "neutral_paraphrase") != writer_prompt("x", 100, "neutral")
