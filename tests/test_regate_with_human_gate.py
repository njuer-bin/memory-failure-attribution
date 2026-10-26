import json

from experiments.regate_with_human_gate import regate


def _row(qid, failure, semantic_correct=False, answer="x"):
    return {
        "question_id": qid,
        "gold_evidence": [{"evidence_id": "e1"}],
        "modes": {
            "real_memory": {
                "formation": {"found": ["e1"], "missing": []},
                "storage": {"found": ["e1"], "missing": []},
                "evolution": {"found": [], "missing": [], "details": {"measured": False}},
                "retrieval": {"found": ["e1"], "missing": []},
                "rerank": {"found": ["e1"], "missing": []},
                "context": {"found": ["e1"], "missing": []},
                "answer": {"answer": answer, "semantic_correct": semantic_correct,
                           "semantic_confidence": "high"},
                "evidence_sufficiency": {"status": "insufficient"},
                "answer_failure_type": failure,
            }
        },
    }


def _write(tmp_path, rows):
    path = tmp_path / "comparison.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return path


def test_human_sufficient_moves_e0_to_reasoning(tmp_path):
    path = _write(tmp_path, [_row("q1", "E0_EVIDENCE_INSUFFICIENT")])
    result = regate(path, {"s1": "sufficient"}, {"s1": "q1"})
    mode = result["per_mode"]["real_memory"]
    assert mode["e0_old"] == 1 and mode["e0_new"] == 0
    assert mode["new_failure_distribution"].get("F6_REASONING_CANDIDATE") == 1


def test_human_insufficient_keeps_e0(tmp_path):
    path = _write(tmp_path, [_row("q1", "F6_REASONING_CANDIDATE")])
    result = regate(path, {"s1": "insufficient"}, {"s1": "q1"})
    mode = result["per_mode"]["real_memory"]
    assert mode["e0_new"] == 1
    assert mode["changed"] == 1


def test_uncovered_question_keeps_stored_label(tmp_path):
    path = _write(tmp_path, [_row("q9", "E0_EVIDENCE_INSUFFICIENT")])
    result = regate(path, {"s1": "sufficient"}, {"s1": "q1"})
    mode = result["per_mode"]["real_memory"]
    assert result["questions_uncovered"] == 1
    assert mode["changed"] == 0
    assert mode["e0_new"] == mode["e0_old"] == 1
