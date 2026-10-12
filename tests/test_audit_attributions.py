from experiments.audit_attributions import F4_WARNING, audit_row


def _row(retrieval_found, retrieval_missing, rerank_found, rerank_missing):
    return {
        "question_id": "test",
        "modes": {
            "real_memory": {
                "answer_failure_type": "F4_RETRIEVAL",
                "retrieval": {"found": retrieval_found, "missing": retrieval_missing},
                "rerank": {"found": rerank_found, "missing": rerank_missing},
            }
        },
    }


def test_f4_accepts_retrieval_loss():
    row = _row([], ["e1"], [], ["e1"])
    assert audit_row(row) == []


def test_f4_accepts_rerank_only_loss():
    row = _row(["e1"], [], [], ["e1"])
    assert audit_row(row) == []


def test_f4_warns_when_both_stages_are_found():
    row = _row(["e1"], [], ["e1"], [])
    assert audit_row(row) == [F4_WARNING]


def test_non_f4_is_ignored():
    row = _row([], ["e1"], [], ["e1"])
    row["modes"]["real_memory"]["answer_failure_type"] = "F5_CONTEXT"
    assert audit_row(row) == []
