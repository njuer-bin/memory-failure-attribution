from evaluation.answer_semantic_eval import (
    _deterministic_support,
    _evidence_text,
    _meaningful_exact_anchor,
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
    support = _deterministic_support("Next month.", evidence)
    assert support is not None
    assert support[0] == "deterministic_temporal"


def test_evaluate_answer_accepts_reference_supported_by_text_field_without_judge():
    evidence = [{
        "text": "Researching adoption agencies — it's been a dream to have a family and give a loving home to kids who need it."
    }]
    result = evaluate_answer("What did Caroline research?", "Caroline researched adoption agencies.", evidence)
    assert result["evidence_sufficient"] is True
    assert result["correct"] is True
    assert result["adjudication"] == "deterministic_lexical"


def test_content_field_remains_supported_for_compatibility():
    evidence = [{"content": "I went to a LGBTQ support group yesterday."}]
    assert _meaningful_exact_anchor("LGBTQ support group", evidence)
