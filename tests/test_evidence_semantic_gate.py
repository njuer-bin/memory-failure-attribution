from evaluation.answer_semantic_eval import _deterministic_support, evaluate_answer


def test_relative_temporal_evidence_is_deterministically_sufficient():
    evidence = [
        {
            "content": "I went to a LGBTQ support group yesterday and it was so powerful.",
            "timestamp": "1:56 pm on 8 May, 2023",
        }
    ]

    result = _deterministic_support("7 May 2023", evidence)

    assert result is not None
    assert result[0] == "deterministic_temporal"
    assert result[1] == "yesterday"


def test_lexical_overlap_alone_does_not_bypass_semantic_judge():
    # A phrase match is not proof that the evidence answers the requested
    # relation. The semantic judge must inspect the question and evidence.
    evidence = [
        {"content": "A review mentioned The Glass Menagerie in passing."},
    ]

    result = _deterministic_support("The Glass Menagerie", evidence)

    assert result is None


def test_unrelated_evidence_does_not_get_deterministic_override():
    evidence = [
        {"content": "Melanie visited the beach last week."},
    ]

    result = _deterministic_support("adoption agencies", evidence)

    assert result is None


def test_contradictory_judge_reason_downgrades_sufficiency(monkeypatch):
    """A judge saying the evidence does not mention the target must not pass E0."""
    monkeypatch.setattr(
        "evaluation.answer_semantic_eval._call_judge",
        lambda prompt: {
            "correct": False,
            "evidence_sufficient": True,
            "confidence": "high",
            "reason": "The evidence does not mention Melanie painting a sunrise.",
        },
    )

    result = evaluate_answer(
        "When did Melanie paint a sunrise?",
        "2022",
        [{"content": "Melanie spoke with her counselor about stress."}],
    )

    assert result["evidence_sufficient"] is False
    assert result["confidence"] == "low"
    assert result["adjudication"] == "semantic_judge"
