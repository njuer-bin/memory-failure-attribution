from experiments.check_v3_annotations import agreement, validate
from experiments.make_v3_annotation_set import build_items, select_records


def _row(i, dimension="epistemic", gold="CERTAIN"):
    return {
        "sample_id": f"s{i}", "dimension": dimension, "proposition": "购买电脑",
        "gold_status": gold, "has_legitimate_update": True,
        "dialogue": "dialogue",
        "paths": {
            path: {"memories": [f"memory-{path}"], "topic_mentioned": True,
                   "spec": {"schedule": [220, 180, 140, 120, 100]}}
            for path in ("S1", "S2", "PEEK", "PARA", "TEMP1", "TEMP2")
        },
    }


def test_select_records_balanced_counts():
    rows = ([_row(i) for i in range(10)] + [_row(100 + i, "intentional") for i in range(10)]
            + [_row(200 + i, "conditional", "CONDITION_ACTIVE") for i in range(10)])
    selected = select_records(rows)
    assert len(selected) == 10
    assert sum(r["dimension"] == "epistemic" for r in selected) == 4
    assert sum(r["dimension"] == "intentional" for r in selected) == 3
    assert sum(r["dimension"] == "conditional" for r in selected) == 3


def test_build_items_sixty_unique_ids():
    rows = ([_row(i) for i in range(10)] + [_row(100 + i, "intentional") for i in range(10)]
            + [_row(200 + i, "conditional", "CONDITION_ACTIVE") for i in range(10)])
    items = build_items(rows, seed=1)
    assert len(items) == 60
    assert len({item["item_id"] for item in items}) == 60
    assert all("gold_status" not in item["target_question"] for item in items)


def test_validate_detects_invalid_primary_judgment():
    rows = [{
        "item_id": "V3C-0001", "proposition_identity": "PRESERVED",
        "primary_judgment": "BAD_LABEL", "confidence": "HIGH",
    }]
    report = validate(rows)
    assert len(report["primary_judgment"]["invalid"]) == 1


def test_agreement_perfect():
    rows = [{
        "item_id": "V3C-0001", "proposition_identity": "PRESERVED",
        "primary_judgment": "NO_DISTORTION", "confidence": "HIGH",
    }]
    result = agreement(rows, rows)
    assert result["fields"]["primary_judgment"]["raw_agreement"] == 1.0
