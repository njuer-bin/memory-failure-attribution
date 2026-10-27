from collections import Counter

from experiments.fact_specs import FACT_SPECS
from experiments.score_fact_annotations import aggregate_row, score


def test_all_required_present_is_sufficient():
    assert aggregate_row([("", True), ("", True)]) == "sufficient"


def test_any_missing_required_is_insufficient():
    assert aggregate_row([("", True), ("", False)]) == "insufficient"


def test_any_of_group_passes_with_one_alternative():
    assert aggregate_row([("g", False), ("g", True)]) == "sufficient"


def test_any_of_group_fails_when_all_absent():
    assert aggregate_row([("g", False), ("g", False)]) == "insufficient"


def test_uncertain_required_propagates_unless_insufficient():
    assert aggregate_row([("", True), ("", "UNC")]) == "uncertain"
    assert aggregate_row([("", False), ("", "UNC")]) == "insufficient"
    assert aggregate_row([("g", "UNC"), ("g", False)]) == "uncertain"


def test_blank_fact_makes_row_unknown():
    assert aggregate_row([("", None)]) is None
    assert aggregate_row([("g", None), ("g", False)]) is None


def test_fact_specs_cover_200_questions():
    assert len(FACT_SPECS) == 200
    assert all(sid.startswith(("longmemeval-", "locomo-")) for sid in FACT_SPECS)


def test_every_question_has_nonempty_facts_and_groups_have_two_members():
    for sid, facts in FACT_SPECS.items():
        assert facts, sid
        assert all(text.strip() for text, _ in facts), sid
        groups = Counter(group for _, group in facts if group)
        assert all(count >= 2 for count in groups.values()), (sid, groups)


def _key(sid, facts, adjudicated="True", stored="sufficient"):
    return [
        {"sample_id": sid, "fact_id": fid, "group": group, "benchmark": sid.split("-")[0],
         "fact_text": "", "stored_gate": stored, "adjudicated_gate": adjudicated}
        for fid, group in facts
    ]


def test_score_acceptance_and_comparison():
    key = (
        _key("locomo-001", [("a", ""), ("b", "")], adjudicated="True")
        + _key("locomo-002", [("c", "")], adjudicated="False", stored="insufficient")
    )
    perfect = {
        "annotator1": {
            "a": {"fact_present_yes_no_uncertain": "yes"},
            "b": {"fact_present_yes_no_uncertain": "yes"},
            "c": {"fact_present_yes_no_uncertain": "no"},
        },
        "annotator2": {
            "a": {"fact_present_yes_no_uncertain": "yes"},
            "b": {"fact_present_yes_no_uncertain": "yes"},
            "c": {"fact_present_yes_no_uncertain": "no"},
        },
    }
    result = score(key, perfect)
    assert result["fact_level"]["kappa"] == 1.0
    assert result["row_level_inter_annotator"]["primary_uncertain_as_insufficient"]["kappa"] == 1.0
    assert result["acceptance"]["passed"] is True
    consensus = result["consensus_vs_adjudicated"]["primary_uncertain_as_insufficient"]
    assert consensus["n"] == 2
    assert consensus["fact_gate"]["f1"] == 1.0


def test_uncertain_rows_are_insufficient_in_primary_mapping():
    key = _key("locomo-001", [("a", "")], adjudicated="False", stored="insufficient")
    labels = {
        "annotator1": {"a": {"fact_present_yes_no_uncertain": "uncertain"}},
        "annotator2": {"a": {"fact_present_yes_no_uncertain": "uncertain"}},
    }
    result = score(key, labels)
    primary = result["consensus_vs_adjudicated"]["primary_uncertain_as_insufficient"]
    sensitivity = result["consensus_vs_adjudicated"]["sensitivity_excluding_uncertain"]
    assert primary["n"] == 1 and primary["fact_gate"]["tp"] == 1
    assert sensitivity["n"] == 0
    assert result["row_level_inter_annotator"]["primary_uncertain_as_insufficient"]["n"] == 1
    assert result["row_level_inter_annotator"]["sensitivity_excluding_uncertain"]["n"] == 0
