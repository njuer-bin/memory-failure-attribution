from experiments.run_oracle_experiments import _context_only_summary


def _row(formation_found, formation_measured):
    return {
        "gold_evidence": [{"evidence_id": "e0"}],
        "modes": {
            "oracle_context": {
                "formation": {"found": formation_found, "details": {"measured": formation_measured}},
                "storage": {"found": [], "details": {"measured": False}},
                "retrieval": {"found": [], "details": {"measured": False}},
                "rerank": {"found": [], "details": {"measured": False}},
                "context": {"found": ["e0"], "details": {}},
            }
        },
    }


def test_context_only_summary_reports_unmeasured_stages_as_none():
    # Oracle Context bypasses formation/retrieval, so those must be None rather
    # than a misleading 0.0 recall.
    summary = _context_only_summary([_row([], False), _row([], False)])
    assert summary["stage_recall"]["formation"] is None
    assert summary["stage_recall"]["retrieval"] is None
    assert summary["stage_recall"]["evolution"] is None
    assert summary["stage_recall"]["context"] == 1.0


def test_context_only_summary_measures_context_supplied_evidence():
    summary = _context_only_summary([_row(["e0"], False)])
    assert summary["stage_recall"]["context"] == 1.0
