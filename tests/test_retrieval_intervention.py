from experiments.retrieval_intervention import (
    content_tokens,
    lexical_overlap,
    rank_items,
    _summary,
)


def _item(content, vector, iid=None):
    return {"id": iid or content, "content": content, "vector": vector}


def test_content_tokens_drop_stopwords_and_short_words():
    assert content_tokens("When did I visit the museum in 2023?") == {"visit", "museum", "2023"}


def test_lexical_overlap_is_question_coverage():
    q = {"museum", "visit", "2023"}
    assert lexical_overlap(q, "museum visit 2023") == 1.0
    assert round(lexical_overlap(q, "I visited the museum in 2023"), 6) == round(2 / 3, 6)
    assert round(lexical_overlap(q, "the museum in 2023"), 6) == round(2 / 3, 6)
    assert lexical_overlap(set(), "anything") == 0.0


def test_alpha_zero_reproduces_dense_ranking():
    items = [_item("unrelated", [0.2, 0.98]),
             _item("museum visit 2023", [1.0, 0.0])]
    ranked = rank_items(items, [1.0, 0.0], {"museum", "visit", "2023"}, alpha=0.0)
    assert [x["content"] for x in ranked] == ["museum visit 2023", "unrelated"]


def test_alpha_one_ranks_by_lexical_overlap():
    items = [_item("unrelated", [1.0, 0.0]),
             _item("museum visit 2023", [0.0, 1.0])]
    ranked = rank_items(items, [1.0, 0.0], {"museum", "visit", "2023"}, alpha=1.0)
    assert [x["content"] for x in ranked] == ["museum visit 2023", "unrelated"]


def test_summary_decision_needs_six_net_flips_and_positive_ci():
    rows = []
    # 6 placebo-wrong -> repaired-correct, 0 losses, 1 concordant-correct.
    for _ in range(6):
        rows.append({"f4": True, "baseline_failure": "F4_RETRIEVAL",
                     "retrieval_recall": {"dense": 0.0, "hybrid": 1.0},
                     "stored_baseline_correct": False,
                     "arms": {"placebo": {"semantic_correct": False},
                              "first_loss": {"semantic_correct": True},
                              "agnostic": {"semantic_correct": True}}})
    rows.append({"f4": True, "baseline_failure": "F4_RETRIEVAL",
                 "retrieval_recall": {"dense": 1.0, "hybrid": 1.0},
                 "stored_baseline_correct": True,
                 "arms": {"placebo": {"semantic_correct": True},
                          "first_loss": {"semantic_correct": True},
                          "agnostic": {"semantic_correct": True}}})
    summary = _summary(rows, alpha=0.5)
    assert summary["primary_f4"]["net_flips"] == 6
    assert summary["decision"]["success"] is True
    assert summary["retrieval_recall_f4"]["dense"] < summary["retrieval_recall_f4"]["hybrid"]
