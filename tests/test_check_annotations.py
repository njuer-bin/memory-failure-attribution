from experiments.check_annotations import cohen_kappa, validate


def test_cohen_kappa_known_value():
    a = ["YES", "NO", "YES"]
    b = ["YES", "NO", "NO"]
    assert abs(cohen_kappa(a, b) - 0.4) < 1e-9


def test_cohen_kappa_perfect():
    assert cohen_kappa(["A", "B", "A"], ["A", "B", "A"]) == 1.0


def test_validate_detects_missing_and_invalid():
    rows = [{
        "trajectory_id": "s", "condition": "raw", "depth": "raw",
        "proposition_identity": "PRESERVED", "polarity": "", "epistemic_status": "MAYBE",
    }]
    report = validate(rows)
    assert report["proposition_identity"]["missing"] == 0
    assert report["polarity"]["missing"] == 1
    assert len(report["epistemic_status"]["invalid"]) == 1
