from evaluation.answer_semantic_eval import (
    _deterministic_support,
    _repair_is_eligible,
)


def test_relative_temporal_evidence_is_deterministically_sufficient():
    evidence = [
        {
            "content": "I went to a LGBTQ support group yesterday and it was so powerful.",
            "timestamp": "1:56 pm on 8 May, 2023",
        }
    ]

    result = _deterministic_support(
        "7 May 2023",
        "When did Caroline go to the LGBTQ support group?",
        evidence,
    )

    assert result is not None
    assert result[0] == "deterministic_temporal"
    assert result[1] == "yesterday"


def test_explicit_answer_phrase_is_deterministically_sufficient():
    evidence = [
        {"content": "Caroline researched adoption agencies."},
    ]

    result = _deterministic_support(
        "Caroline researched adoption agencies.",
        "What did Caroline research?",
        evidence,
    )

    assert result is not None
    assert result[0] == "deterministic_lexical"
    assert result[1] == "caroline researched adoption agencies"


def test_unrelated_evidence_does_not_get_deterministic_override():
    evidence = [
        {"content": "Melanie visited the beach last week."},
    ]

    result = _deterministic_support(
        "adoption agencies", "Where did I volunteer?", evidence,
    )

    assert result is None


# Audit C5 residual: the post-judge lexical repair accepted model refusals
# that happened to contain an evidence phrase ("...does not provide a house").
def test_refusal_is_not_repair_eligible():
    assert not _repair_is_eligible(
        "The evidence does not provide information about a house.",
        "When did I buy the house?",
    )
    assert not _repair_is_eligible("I cannot determine that from the evidence.", "What did I buy?")
    assert not _repair_is_eligible("No information about the concert.", "Which concert did I attend?")


def test_unrelated_candidate_is_not_repair_eligible():
    assert not _repair_is_eligible("adoption agencies", "Where did I volunteer?")


def test_temporal_answer_to_temporal_question_is_repair_eligible():
    assert _repair_is_eligible("7 days", "How long after the market did I buy it?")


def test_temporal_answer_to_non_temporal_question_is_not_repair_eligible():
    assert not _repair_is_eligible("last week", "Which cafe did I visit?")
