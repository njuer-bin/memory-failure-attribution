from __future__ import annotations

from collections import Counter

from experiments.audit_stage_labels import (
    _dist,
    _per_class,
    _simulate,
    _to_pilot,
    audit,
)


def test_per_class_metrics_handles_missing_predictions():
    pairs = [("formation", "formation"), ("e0", "retrieval"), ("retrieval", "retrieval")]
    metrics = _per_class(pairs, ["formation", "retrieval", "e0"])
    assert metrics["formation"]["precision"] == 1.0
    assert metrics["formation"]["recall"] == 1.0
    # e0 is never predicted by the automatic labels.
    assert metrics["e0"]["precision"] is None
    assert metrics["e0"]["recall"] == 0.0
    # retrieval's precision is hurt by the mis-mapped e0 row.
    assert abs(metrics["retrieval"]["precision"] - 0.5) < 1e-9


def test_to_pilot_maps_full_labels():
    assert _to_pilot(["F1_FORMATION", "F4_RETRIEVAL", "E0_EVIDENCE_INSUFFICIENT",
                      "F6_REASONING_CANDIDATE", "EVAL_SEMANTIC_UNCERTAIN", "none"]) == [
        "formation", "retrieval", "e0", "none", "eval", "none",
    ]


def test_dist_reports_dominant_class():
    dist = _dist(["retrieval", "retrieval", "formation"])
    assert dist["dominant"] == "retrieval"
    assert dist["shares"]["retrieval"] == 2 / 3


def test_simulate_zero_noise_is_deterministic():
    la = ["retrieval"] * 20 + ["formation"] * 5 + ["none"] * 5
    lb = ["retrieval"] * 10 + ["formation"] * 15 + ["none"] * 5
    mapping = {"retrieval": Counter({"retrieval": 3})}
    out = _simulate(la, lb, 0.0, "empirical", mapping, ["retrieval", "formation", "none"],
                    sims=5, seed=0)
    assert out["survival_p05"] in (0.0, 1.0)
    assert out["median_p"] == out["p90"]


def _toy_inputs():
    key = {}
    a_sheet = {}
    b_sheet = {}
    for i in range(10):
        rid = f"r{i}"
        system = "semantic" if i < 5 else "verbatim"
        auto = "F1_FORMATION" if system == "semantic" else "F4_RETRIEVAL"
        key[rid] = {"row_id": rid, "system": system, "auto_first_loss": auto}
        human = ("formation" if system == "semantic" else "retrieval") if i % 3 else "e0"
        a_sheet[rid] = {"row_id": rid, "annotated_first_loss_stage": human}
        b_sheet[rid] = {"row_id": rid, "annotated_first_loss_stage": human}
    fingerprint = {}
    for i in range(8):
        qid = f"q{i}"
        fingerprint[qid] = {
            "question_id": qid,
            "modes": {
                "semantic": {"answer_failure_type": "F1_FORMATION" if i < 4 else "none"},
                "verbatim": {"answer_failure_type": "F4_RETRIEVAL" if i < 4 else "none"},
            },
        }
    return key, {"a": a_sheet, "b": b_sheet}, fingerprint


def test_audit_end_to_end_structure():
    key, labels, fingerprint = _toy_inputs()
    result = audit(key, labels, fingerprint, bootstrap_repeats=20, sims=5)
    assert result["n_valid"] == 10
    assert "a" in result["auto_vs_human"] and "b" in result["auto_vs_human"]
    assert result["pilot_system_distributions"]["semantic"]["auto"]["dominant"] == "formation"
    pair = result["fingerprint_sensitivity"]["semantic_vs_verbatim"]
    assert pair["baseline_p_full_labels"] is not None
    assert {s["q"] for s in pair["simulations"]} == {0.1, 0.2, 0.3, 0.5}
