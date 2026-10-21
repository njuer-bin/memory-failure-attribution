from evaluation.answer_semantic_eval import (
    _deterministic_support,
    _evidence_text,
    _meaningful_exact_anchor,
    _prompt,
    _reason_indicates_insufficient_evidence,
    evaluate_answer,
)


def test_evidence_text_reads_normalized_text_field():
    evidence = [{
        "text": "Researching adoption agencies — it's been a dream to have a family.",
        "timestamp": "1:00 pm on 25 May, 2023",
    }]
    rendered = _evidence_text(evidence)
    assert "Researching adoption agencies" in rendered
    assert "timestamp=1:00 pm on 25 May, 2023" in rendered


def test_meaningful_anchor_reads_text_field():
    evidence = [{"text": "I'm keen on counseling or working in mental health."}]
    assert _meaningful_exact_anchor("counseling or working in mental health", evidence)


def test_deterministic_support_reads_text_field():
    evidence = [{
        "text": "We're thinking about going camping next month.",
        "timestamp": "1:00 pm on 25 May, 2023",
    }]
    support = _deterministic_support(
        "Next month.", "When are we going camping?", evidence,
    )
    assert support is not None
    assert support[0] == "deterministic_temporal"


def test_evaluate_answer_accepts_reference_supported_by_text_field_without_judge():
    evidence = [{
        "text": "Caroline researched adoption agencies and it's been a dream to give a loving home to kids who need it."
    }]
    result = evaluate_answer("What did Caroline research?", "Caroline researched adoption agencies.", evidence)
    assert result["evidence_sufficient"] is True
    assert result["correct"] is True
    assert result["adjudication"] == "deterministic_lexical"


def test_content_field_remains_supported_for_compatibility():
    evidence = [{"content": "I went to a LGBTQ support group yesterday."}]
    assert _meaningful_exact_anchor("LGBTQ support group", evidence)


def test_reason_insufficiency_detector_is_defined_and_matches():
    # Regression: this helper was accidentally orphaned, which raised NameError
    # inside evaluate_answer and silently turned gate verdicts into errors.
    assert _reason_indicates_insufficient_evidence("This mentions a different event.")
    assert not _reason_indicates_insufficient_evidence("The evidence matches the reference.")


def test_prompt_labels_reference_and_model_answers_differently():
    evidence = [{"text": "Caroline researched adoption agencies."}]
    reference_prompt = _prompt("What did Caroline research?", "adoption agencies", evidence, candidate_is_reference=True)
    model_prompt = _prompt("What did Caroline research?", "adoption agencies", evidence, candidate_is_reference=False)
    assert "benchmark reference answer" in reference_prompt
    assert "model-generated answer, not the benchmark reference" in model_prompt
    # The model-answer prompt must not tell the judge the candidate is the reference.
    assert "is the benchmark reference answer. Do not assume" not in model_prompt



def _stub_judge(monkeypatch, payload: str):
    import json
    import evaluation.answer_semantic_eval as mod

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return json.dumps({"response": payload}).encode("utf-8")

    monkeypatch.setattr(mod.urllib.request, "urlopen", lambda *a, **k: _Response())


def test_evaluate_answer_post_judge_path_runs_offline(monkeypatch):
    # Exercises the full judge path with a stub, catching NameError-style
    # breakage that pure-helper tests miss.
    _stub_judge(
        monkeypatch,
        '{"correct": false, "evidence_sufficient": true, "confidence": "high", "reason": "wrong."}',
    )
    evidence = [{"text": "Caroline researched adoption agencies."}]
    result = evaluate_answer("What did Caroline research?", "Something unrelated entirely.", evidence)
    assert result["evidence_sufficient"] is True
    assert result["correct"] is False
    assert result["confidence"] == "high"


def test_evaluate_answer_insufficient_reason_forces_insufficient(monkeypatch):
    _stub_judge(
        monkeypatch,
        '{"correct": true, "evidence_sufficient": true, "confidence": "high", '
        '"reason": "It mentions a different event than the question asks about."}',
    )
    evidence = [{"text": "I attended a fundraising dinner for the local animal shelter."}]
    result = evaluate_answer("Where did I volunteer?", "The local animal shelter.", evidence)
    assert result["evidence_sufficient"] is False
    assert result["correct"] is False
