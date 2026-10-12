from __future__ import annotations

import json

from experiments.rescore_existing_results import rescore


def _row(question_id: str, prediction: str, reference: str) -> dict:
    gold = [{"evidence_id": "e1", "text": "gold evidence"}]
    stage = {"found": ["e1"], "missing": [], "details": {}}
    answer = {
        "answer": prediction,
        "correct": False,
        "exact_match": 0.0,
        "token_f1": 0.0,
        "threshold": 0.5,
        "temporal_equivalent": False,
        "temporal_anchor_date": None,
        "phrase_match": False,
        "explicit_date_mismatch": False,
    }
    mode = {
        "formation": stage,
        "storage": stage,
        "evolution": stage,
        "retrieval": stage,
        "rerank": stage,
        "context": stage,
        "answer": answer.copy(),
        "evidence_sufficiency": {"status": "sufficient"},
        "answer_failure_type": "F6_REASONING",
    }
    oracle_context = {**mode, "answer": answer.copy()}
    oracle_context["mode"] = "oracle_context"
    return {
        "question_id": question_id,
        "question": "When did Caroline join?",
        "gold_answer": reference,
        "gold_evidence": gold,
        "modes": {
            "real_memory": mode,
            "oracle_memory": {**mode, "answer": answer.copy()},
            "oracle_context": oracle_context,
        },
    }


def test_rescore_reclassifies_reference_anchored_last_weekend(tmp_path):
    source = tmp_path / "comparison.jsonl"
    output = tmp_path / "rescored.jsonl"
    summary = tmp_path / "summary.json"
    row = _row(
        "conv-26#q0027",
        "Last weekend.",
        "The weekend before 17 July 2023 / From July 15, 2023 to July 16, 2023",
    )
    source.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")

    result = rescore(source, output, summary)

    saved = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
    real = saved["modes"]["real_memory"]
    assert real["answer"]["temporal_equivalent"] is True
    assert real["answer"]["correct"] is True
    assert real["answer_failure_type"] is None
    assert result["answer_scoring"]["first_answer_failure_distribution"] == {}


def test_rescore_reclassifies_reference_anchored_last_tuesday(tmp_path):
    source = tmp_path / "comparison.jsonl"
    output = tmp_path / "rescored.jsonl"
    summary = tmp_path / "summary.json"
    row = _row(
        "conv-26#q0031",
        "Last Tuesday.",
        "The Tuesday before 20 July 2023 / July 18, 2023",
    )
    source.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")

    rescore(source, output, summary)

    saved = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
    real = saved["modes"]["real_memory"]
    assert real["answer"]["temporal_equivalent"] is True
    assert real["answer"]["correct"] is True
    assert real["answer_failure_type"] is None
