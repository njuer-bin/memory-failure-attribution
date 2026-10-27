import json

from experiments import judge_reliability as jr


def _row() -> dict:
    return {
        "question_id": "q1",
        "question": "When did Caroline go?",
        "gold_answer": "7 May 2023",
        "gold_evidence": [
            {"evidence_id": "e0", "text": "Caroline went yesterday.",
             "source_id": "D1", "turn_id": "D1:turn_2"},
        ],
        "modes": {
            "real_memory": {
                "answer": {
                    "answer": "7 May 2023",
                    "semantic_correct": False,
                    "semantic_judge_correct": False,
                    "semantic_reason": "stored reason",
                },
                "evidence_sufficiency": {"status": "sufficient", "evidence_sufficient": True,
                                         "reason": "gate"},
            },
            "oracle_memory": {"answer": {"answer": "unrelated", "correct": True}},
            "oracle_context": {"answer": {}},                      # empty answer
        },
    }


def _run(monkeypatch, tmp_path, rows, verdict):
    seen: list[dict] = []

    def fake_evaluate_answer(question, candidate, evidence, **kwargs):
        seen.append({"question": question, "candidate": candidate,
                     "evidence": evidence, "kwargs": kwargs})
        return dict(verdict)

    monkeypatch.setattr(jr, "evaluate_answer", fake_evaluate_answer)
    inp = tmp_path / "comparison.jsonl"
    inp.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                   encoding="utf-8")
    out = tmp_path / "judge_reliability.json"
    monkeypatch.setattr("sys.argv", ["judge_reliability", "--input", str(inp),
                                     "--output", str(out)])
    jr.main()
    return seen, json.loads(out.read_text(encoding="utf-8"))


def test_gate_is_rejudged_with_the_reference_prompt_role(monkeypatch, tmp_path):
    seen, summary = _run(
        monkeypatch, tmp_path, [_row()],
        {"correct": True, "judge_correct": True, "evidence_sufficient": True,
         "confidence": "high", "reason": "ok", "adjudication": "judge", "model": "stub"},
    )
    answer_calls = [c for c in seen if c["kwargs"].get("candidate_is_reference") is not True]
    gate_calls = [c for c in seen if c["kwargs"].get("candidate_is_reference") is True]
    assert [c["candidate"] for c in answer_calls] == ["7 May 2023"]
    assert [c["candidate"] for c in gate_calls] == ["7 May 2023"]
    assert summary["prompt_roles"]["gate_judge"] == "benchmark_reference"


def test_gold_evidence_is_passed_through_verbatim(monkeypatch, tmp_path):
    seen, _ = _run(
        monkeypatch, tmp_path, [_row()],
        {"correct": True, "judge_correct": True, "evidence_sufficient": True,
         "confidence": "high", "reason": "ok", "adjudication": "judge", "model": "stub"},
    )
    assert seen[0]["evidence"] == _row()["gold_evidence"]


def test_lexically_skipped_judgments_stay_out_of_the_agreement_n(monkeypatch, tmp_path):
    # Only real_memory carries a stored verdict; oracle_memory was skipped for
    # lexical correctness and oracle_context has no answer at all.
    _, summary = _run(
        monkeypatch, tmp_path, [_row()],
        {"correct": True, "judge_correct": True, "evidence_sufficient": True,
         "confidence": "high", "reason": "ok", "adjudication": "judge", "model": "stub"},
    )
    assert summary["lexically_skipped_judgments"] == 1
    assert summary["unjudged_answers"] == 1
    assert summary["correct_verdict"]["n"] == 1
    assert summary["correct_verdict"]["n_stored_true"] == 0
    assert summary["raw_judge"]["n"] == 1
    assert summary["n_flips"] == 1
    assert summary["flips"][0]["mode"] == "real_memory"


def test_gate_flip_is_reported_separately_from_answer_flips(monkeypatch, tmp_path):
    _, summary = _run(
        monkeypatch, tmp_path, [_row()],
        {"correct": True, "judge_correct": True, "evidence_sufficient": False,
         "confidence": "high", "reason": "not sufficient", "adjudication": "judge",
         "model": "stub"},
    )
    assert summary["n_gate_flips"] == 1
    assert summary["gate_flips"][0]["stored_evidence_sufficient"] is True
    assert summary["gate_flips"][0]["rerun_evidence_sufficient"] is False
    assert summary["evidence_sufficiency"]["n"] == 1
