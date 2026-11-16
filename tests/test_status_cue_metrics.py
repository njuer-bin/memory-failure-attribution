from evaluation.status_cue_metrics import cue_state


def test_epistemic_certain():
    assert cue_state("用户确认会购买电脑", "epistemic", "CERTAIN") == "MATCH"
    assert cue_state("用户可能购买电脑", "epistemic", "CERTAIN") == "OPPOSITE"
    assert cue_state("用户还没有确认会购买电脑", "epistemic", "CERTAIN") == "OPPOSITE"
    assert cue_state("购买电脑，天气多变", "epistemic", "CERTAIN") == "ABSENT"


def test_epistemic_possible():
    assert cue_state("用户可能会购买电脑", "epistemic", "POSSIBLE") == "MATCH"
    assert cue_state("用户确认会购买电脑", "epistemic", "POSSIBLE") == "OPPOSITE"
    assert cue_state("购买电脑，天气多变", "epistemic", "POSSIBLE") == "ABSENT"


def test_intentional():
    assert cue_state("用户决定购买电脑", "intentional", "COMMITTED") == "MATCH"
    assert cue_state("用户考虑购买电脑", "intentional", "COMMITTED") == "OPPOSITE"
    assert cue_state("用户尚未决定", "intentional", "COMMITTED") == "OPPOSITE"
    assert cue_state("购买电脑，天气多变", "intentional", "COMMITTED") == "ABSENT"
    assert cue_state("用户考虑购买电脑", "intentional", "CONSIDERING") == "MATCH"
    assert cue_state("用户决定购买电脑", "intentional", "CONSIDERING") == "OPPOSITE"


def test_mixed_cues():
    assert cue_state("确认去上海工作，考虑不确定性", "epistemic", "CERTAIN") == "MIXED"
    assert cue_state("考虑购买电脑，已决定推进", "intentional", "COMMITTED") == "MIXED"


def test_conditional_is_na():
    assert cue_state("条件已满足", "conditional", "CONDITION_SATISFIED") == "NA"
