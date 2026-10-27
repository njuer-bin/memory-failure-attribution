from experiments.score_stage_annotations import kappa_multi, score


def test_kappa_multi_perfect_and_known_example():
    assert kappa_multi(["a", "b", "a"], ["a", "b", "a"]) == 1.0
    # po=0.75, pe=0.5 -> kappa=0.5
    assert kappa_multi(["a", "a", "b", "b"], ["a", "a", "a", "b"]) == 0.5


def test_score_excludes_invalid_evolution_and_reports_confusion():
    key = {
        "r1": {"auto_first_loss": "F1_FORMATION"},
        "r2": {"auto_first_loss": "F4_RETRIEVAL"},
        "r3": {"auto_first_loss": "none"},
    }
    a = {
        "r1": {"annotated_first_loss_stage": "formation"},
        "r2": {"annotated_first_loss_stage": "evolution"},
        "r3": {"annotated_first_loss_stage": "none"},
    }
    b = {
        "r1": {"annotated_first_loss_stage": "formation"},
        "r2": {"annotated_first_loss_stage": "retrieval"},
        "r3": {"annotated_first_loss_stage": "none"},
    }
    result = score(key, {"a": a, "b": b})
    assert result["valid_co_decided"] == 2
    assert result["invalid_or_missing"]["a"] == {"evolution": 1}
    assert result["human_human"]["kappa_multi"] == 1.0
    assert result["acceptance"]["passed"] is True
