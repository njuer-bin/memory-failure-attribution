from evaluation.status_sidecar import parse_sidecar, sidecar_present, sidecar_status


def test_parse_sidecar_ascii_and_fullwidth():
    text = "记忆。\n[状态: 确定性=已确认；意图=不适用；条件=不适用]"
    fields = parse_sidecar(text)
    assert fields == {"确定性": "已确认", "意图": "不适用", "条件": "不适用"}
    assert sidecar_present(text)


def test_sidecar_status_by_dimension():
    assert sidecar_status("[状态: 确定性=已确认]", "epistemic") == "CERTAIN"
    assert sidecar_status("[状态：确定性=可能]", "epistemic") == "POSSIBLE"
    assert sidecar_status("[状态: 意图=已决定]", "intentional") == "COMMITTED"
    assert sidecar_status("[状态: 意图=考虑中]", "intentional") == "CONSIDERING"
    assert sidecar_status("[状态: 条件=已满足]", "conditional") == "CONDITION_SATISFIED"
    assert sidecar_status("[状态: 条件=未满足]", "conditional") == "CONDITION_ACTIVE"


def test_missing_sidecar_returns_none():
    assert parse_sidecar("没有状态行") is None
    assert not sidecar_present("没有状态行")
    assert sidecar_status("没有状态行", "epistemic") is None


def test_unrelated_field_returns_none():
    assert sidecar_status("[状态: 意图=已决定]", "epistemic") is None


def test_last_sidecar_wins():
    text = "[状态: 确定性=可能]\n[状态: 确定性=已确认]"
    assert sidecar_status(text, "epistemic") == "CERTAIN"
