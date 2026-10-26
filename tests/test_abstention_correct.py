from experiments.abstention_correct import (
    correct_row,
    failure_distribution,
    gold_is_abstention,
    is_abstention,
)


def _row(answer, gold_answer="a cup", gold_id="e1", mode="real_memory"):
    return {
        "question_id": "q1",
        "gold_answer": gold_answer,
        "gold_evidence": [{"evidence_id": gold_id}],
        "modes": {
            mode: {
                "formation": {"found": [gold_id], "missing": []},
                "storage": {"found": [gold_id], "missing": []},
                "evolution": {"found": [], "missing": [], "details": {"measured": False}},
                "retrieval": {"found": [gold_id], "missing": []},
                "rerank": {"found": [gold_id], "missing": []},
                "context": {"found": [gold_id], "missing": []},
                "answer": {"answer": answer, "semantic_correct": True,
                           "semantic_confidence": "high"},
                "evidence_sufficiency": {"status": "sufficient"},
                "answer_failure_type": None,
            }
        },
    }


def test_whole_answer_abstentions_detected():
    for text in ["Unknown.", "Not mentioned.", "Cannot be determined.",
                 "It is not stated.", "Not enough information.",
                 "Cannot be determined from the evidence."]:
        assert is_abstention(text), text


def test_partial_or_substantive_answers_not_abstentions():
    for text in ["30 minutes of jogging; yoga hours are not specified.",
                 "7 May 2023", "", "Not mentioned but she went on Tuesday."]:
        assert not is_abstention(text), text


def test_gold_abstention_phrasings():
    assert gold_is_abstention("The information provided is not enough. You only mentioned booking.")
    assert gold_is_abstention("Not mentioned.")
    # Concrete gold that merely contains "did not mention" is not an abstention.
    assert not gold_is_abstention("0. You did not mention visiting any museum in December")
    assert not gold_is_abstention("7 May 2023")


def test_flip_only_when_reference_is_concrete():
    concrete = _row("Cannot be determined.")
    assert correct_row(concrete) == 1
    answer = concrete["modes"]["real_memory"]["answer"]
    assert answer["semantic_correct"] is False
    assert answer["_abstention_flip"] is True
    # All gold evidence reached context -> abstention becomes a reasoning candidate.
    assert concrete["modes"]["real_memory"]["answer_failure_type"] == "F6_REASONING_CANDIDATE"


def test_no_flip_when_reference_is_an_abstention():
    row = _row("Cannot be determined.", gold_answer="The information provided is not enough. You did not say.")
    assert correct_row(row) == 0
    assert row["modes"]["real_memory"]["answer"]["semantic_correct"] is True


def test_no_flip_when_answer_is_substantive():
    row = _row("7 May 2023")
    assert correct_row(row) == 0


def test_failure_distribution_counts_none():
    assert failure_distribution([_row("7 May 2023")]) == {
        "real_memory": {"none": 1}
    }


def test_validate_abstention_rule_separates_guarded_from_naive():
    from experiments.validate_abstention_rule import validate

    key = {
        "locomo-001": {"stored_semantic_correct": "True"},
        "longmemeval-001": {"stored_semantic_correct": "True"},
    }
    adj = {
        "locomo-001": {"adj_answer_correct": "False"},
        "longmemeval-001": {"adj_answer_correct": "True"},
    }
    ann = {
        "locomo-001": {"model_answer": "Not mentioned.", "reference_answer": "a dog"},
        "longmemeval-001": {
            "model_answer": "Cannot be determined.",
            "reference_answer": "The information provided is not enough. You did not say.",
        },
    }
    result = validate(key, adj, ann)
    assert result["stored_correct_sample"] == 2
    assert result["abstention_style_rows"] == 2
    assert result["naive_rule"]["tp"] == 1 and result["naive_rule"]["fp"] == 1
    assert result["naive_rule"]["precision"] == 0.5
    assert result["guarded_rule"]["tp"] == 1 and result["guarded_rule"]["fp"] == 0
    assert result["guarded_rule"]["precision"] == 1.0
    assert result["abstention_subset_2x2"]["precision"] == 1.0
