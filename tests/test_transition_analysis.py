from experiments.analyze_transitions import evidence_level_transition_stats, transition_stats


def _row(gate="sufficient", found=None):
    found = found or {}
    return {
        "gold_evidence": [{"evidence_id": "e0"}],
        "modes": {
            "real_memory": {
                "evidence_sufficiency": {"status": gate},
                **{stage: {"found": found.get(stage, [])} for stage in (
                    "formation", "storage", "evolution", "retrieval", "rerank", "context"
                )},
            }
        },
    }


def test_question_level_transition_excludes_upstream_losses():
    rows = [
        _row(found={
            "formation": ["e0"], "storage": ["e0"], "evolution": ["e0"],
            "retrieval": [], "rerank": [], "context": [],
        }),
        _row(found={
            "formation": [], "storage": [], "evolution": [],
            "retrieval": [], "rerank": [], "context": [],
        }),
    ]
    report = transition_stats(rows, gate_sufficient_only=True)
    assert report["eligible_rows"] == 2
    assert report["transitions"]["formation_to_storage"]["conditional_survival"] == 1.0
    assert report["transitions"]["evolution_to_retrieval"]["eligible_after_previous"] == 1
    assert report["transitions"]["evolution_to_retrieval"]["conditional_survival"] == 0.0


def test_gate_sufficient_filter_excludes_e0_rows():
    rows = [
        _row(gate="sufficient", found={"formation": ["e0"], "storage": ["e0"]}),
        _row(gate="insufficient", found={"formation": [], "storage": []}),
    ]
    report = transition_stats(rows, gate_sufficient_only=True)
    assert report["eligible_rows"] == 1
    assert report["stage"]["formation"]["passed"] == 1


def test_evidence_level_transition_handles_partial_multi_evidence_cases():
    row = {
        "gold_evidence": [{"evidence_id": "e0"}, {"evidence_id": "e1"}],
        "modes": {"real_memory": {
            "evidence_sufficiency": {"status": "sufficient"},
            "formation": {"found": ["e0", "e1"]},
            "storage": {"found": ["e0", "e1"]},
            "evolution": {"found": ["e0"]},
            "retrieval": {"found": ["e0"]},
            "rerank": {"found": ["e0"]},
            "context": {"found": ["e0"]},
        }},
    }
    report = evidence_level_transition_stats([row], gate_sufficient_only=True)
    assert report["eligible_evidence"] == 2
    assert report["transitions"]["formation_to_storage"]["conditional_survival"] == 1.0
    assert report["transitions"]["storage_to_evolution"]["conditional_survival"] == 0.5
