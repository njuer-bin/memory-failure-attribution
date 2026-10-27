import json

from experiments import rescore_answers as rs

NUMERIC_GOLD = "7 days. 8 days (including the last day) is also acceptable."
QUESTION = "How many days before the party did I order the gift?"


def _stored(**overrides):
    answer = {
        "answer": "7 days", "correct": False, "exact_match": 0.0, "token_f1": 0.0,
        "semantic_correct": True, "semantic_judge_correct": True,
        "semantic_evidence_sufficient": True, "semantic_confidence": "high",
        "semantic_reason": "stored", "semantic_adjudication": "judge",
    }
    answer.update(overrides)
    return answer


def _forbid_judge(monkeypatch):
    import evaluation.answer_semantic_eval as mod

    def _explode(*args, **kwargs):
        raise AssertionError("the judge must not be consulted for this answer")

    monkeypatch.setattr(mod.urllib.request, "urlopen", _explode)


def _stub_judge(monkeypatch, correct: bool):
    import evaluation.answer_semantic_eval as mod

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return json.dumps({"response": json.dumps({
                "correct": correct, "evidence_sufficient": True,
                "confidence": "high", "reason": "stub",
            })}).encode("utf-8")

    monkeypatch.setattr(mod.urllib.request, "urlopen", lambda *a, **k: _Response())


def test_numeric_layer_overrides_a_stored_judge_false_positive(monkeypatch):
    _forbid_judge(monkeypatch)
    out = rs.rescore_answer(QUESTION, _stored(answer="15"), [{"text": "7 days before."}], NUMERIC_GOLD)
    assert out["semantic_correct"] is False
    assert out["semantic_adjudication"] == "deterministic_numeric_range"
    assert out["semantic_judge_correct"] is None


def test_numeric_layer_repairs_a_stored_judge_false_negative(monkeypatch):
    _forbid_judge(monkeypatch)
    stored = _stored(answer="One week.", semantic_correct=False, semantic_judge_correct=False)
    out = rs.rescore_answer(QUESTION, stored, [{"text": "7 days before."}], NUMERIC_GOLD)
    assert out["semantic_correct"] is True


def test_stored_judge_verdict_is_reused_for_non_numeric_answers(monkeypatch):
    _forbid_judge(monkeypatch)
    stored = _stored(answer="Fixing the fence.", semantic_correct=False,
                     semantic_judge_correct=False, semantic_reason="stored reason")
    out = rs.rescore_answer("What did I do?", stored, [{"text": "Fixing the fence."}], "Fixing the fence")
    assert out["semantic_correct"] is False
    assert out["semantic_reason"] == "stored reason"


def test_previously_lexically_skipped_answer_is_now_judged(monkeypatch):
    # token-F1 0.5 no longer skips the judge (audit C5), and the reference here is
    # not numeric, so the judge is the layer that has to decide.
    _stub_judge(monkeypatch, correct=False)
    stored = {
        "answer": "Fixing the gate", "correct": True, "exact_match": 0.0, "token_f1": 0.5,
        "semantic_correct": None, "semantic_judge_correct": None,
    }
    out = rs.rescore_answer("What did I do?", stored, [{"text": "Fixing the fence."}], "Fixing the fence")
    assert out["semantic_correct"] is False


def test_safe_lexical_skip_still_avoids_the_judge(monkeypatch):
    _forbid_judge(monkeypatch)
    stored = {
        "answer": "Fixing the fence", "correct": True, "exact_match": 1.0, "token_f1": 1.0,
        "semantic_correct": None, "semantic_judge_correct": None,
    }
    out = rs.rescore_answer("What did I do?", stored, [{"text": "Fixing the fence."}], "Fixing the fence")
    assert out["semantic_correct"] is None


def test_rejudge_everything_consults_the_judge_again(monkeypatch):
    _stub_judge(monkeypatch, correct=True)
    stored = _stored(answer="Something else entirely", semantic_correct=False,
                     semantic_judge_correct=False)
    out = rs.rescore_answer("What did I do?", stored, [{"text": "Fixing the fence."}],
                            "Fixing the fence", rejudge_everything=True)
    assert out["semantic_correct"] is True


def test_rescore_row_recomputes_attribution_from_the_stored_traces(monkeypatch):
    _forbid_judge(monkeypatch)
    stages = {
        stage: {"found": ["e0"]}
        for stage in ("formation", "storage", "retrieval", "rerank", "context")
    }
    row = {
        "question_id": "q1", "question": QUESTION, "gold_answer": NUMERIC_GOLD,
        "gold_evidence": [{"evidence_id": "e0", "text": "7 days before."}],
        "modes": {
            "real_memory": {
                **stages,
                "answer": _stored(answer="15"),
                "evidence_sufficiency": {"status": "sufficient", "evidence_sufficient": True,
                                         "confidence": "high", "reason": "gate"},
                "answer_failure_type": None, "failure_type": None,
            },
        },
    }
    out = rs.rescore_row(row)
    # Evidence reached the context and the number is wrong: that is a reasoning
    # failure, not the "no failure" the judge's false positive had recorded.
    assert out["modes"]["real_memory"]["answer_failure_type"] == "F6_REASONING_CANDIDATE"
    assert out["modes"]["real_memory"]["failure_type"] == "F6_REASONING_CANDIDATE"


def test_ordering_refutation_flips_a_stored_judge_false_positive(monkeypatch):
    _forbid_judge(monkeypatch)
    question = (
        "Which event did I attend first, the 'Effective Time Management' "
        "workshop or the 'Data Analysis using Python' webinar?"
    )
    gold = [
        {
            "evidence_id": "e1", "text":
            "I've been attending workshops, like the workshop on 'Effective Time "
            "Management' at the local community center last Saturday.",
            "timestamp": "2023/05/28 (Sun) 21:04",
        },
        {
            "evidence_id": "e2", "text":
            "I participated in a webinar on 'Data Analysis using Python' two months ago.",
            "timestamp": "2023/05/28 (Sun) 07:17",
        },
    ]
    stored = _stored(answer="The 'Effective Time Management' workshop.")
    flip = rs._apply_ordering_refutation(question, stored, gold)
    assert flip is not None
    assert flip["semantic_correct"] is False
    assert flip["semantic_adjudication"] == "ordering_refutation"


def test_ordering_refutation_spares_other_adjudications_and_non_judges():
    question = (
        "Which event did I attend first, the 'Effective Time Management' "
        "workshop or the 'Data Analysis using Python' webinar?"
    )
    gold = [
        {"text": "workshop last Saturday", "timestamp": "2023/05/28 (Sun) 21:04"},
        {"text": "a webinar on 'Data Analysis using Python' two months ago",
         "timestamp": "2023/05/28 (Sun) 07:17"},
    ]
    assert rs._apply_ordering_refutation(
        question, _stored(semantic_adjudication="deterministic_lexical"), gold
    ) is None
    assert rs._apply_ordering_refutation(
        question, _stored(semantic_correct=False), gold
    ) is None
    assert rs._apply_ordering_refutation(
        "What color is the sky?", _stored(answer="blue"), gold
    ) is None


def test_rescore_row_applies_the_refutation_flag(monkeypatch):
    _forbid_judge(monkeypatch)
    question = (
        "Which event did I attend first, the 'Effective Time Management' "
        "workshop or the 'Data Analysis using Python' webinar?"
    )
    gold = [
        {
            "evidence_id": "e1", "text":
            "I've been attending workshops, like the workshop on 'Effective Time "
            "Management' at the local community center last Saturday.",
            "timestamp": "2023/05/28 (Sun) 21:04",
        },
        {
            "evidence_id": "e2", "text":
            "I participated in a webinar on 'Data Analysis using Python' two months ago.",
            "timestamp": "2023/05/28 (Sun) 07:17",
        },
    ]
    stages = {
        stage: {"found": ["e1", "e2"]}
        for stage in ("formation", "storage", "retrieval", "rerank", "context")
    }
    row = {
        "question_id": "q1", "question": question,
        "gold_answer": "'Data Analysis using Python' webinar",
        "gold_evidence": gold,
        "modes": {
            "real_memory": {
                **stages,
                "answer": _stored(answer="The 'Effective Time Management' workshop."),
                "evidence_sufficiency": {"status": "sufficient", "evidence_sufficient": True,
                                         "confidence": "high", "reason": "gate"},
                "answer_failure_type": None, "failure_type": None,
            },
        },
    }
    out = rs.rescore_row(row, apply_ordering_refutation=True)
    mode = out["modes"]["real_memory"]
    assert mode["answer"]["semantic_adjudication"] == "ordering_refutation"
    assert mode["answer_failure_type"] == "F6_REASONING_CANDIDATE"
    assert mode["failure_type"] == "F6_REASONING_CANDIDATE"
