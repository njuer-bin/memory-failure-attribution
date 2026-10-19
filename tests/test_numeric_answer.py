from evaluation.answer_semantic_eval import evaluate_answer
from evaluation.numeric_answer import gold_numeric_range, numeric_verdict
from experiments.run_oracle_experiments import _lexical_skip_is_safe


def test_numbers_inside_identifiers_times_and_dates_are_not_quantities():
    # Regression: "S22" (a phone model), "6:45" (a time) and "3/22" (a date) were
    # read as counts, which produced confident wrong verdicts on non-numeric rows.
    assert gold_numeric_range("Samsung Galaxy S22") is None
    assert gold_numeric_range("6:45 AM") is None
    assert gold_numeric_range("3/22") is None
    assert numeric_verdict("Samsung Galaxy S22", "Which phone did I buy?", "Dell XPS 13") is None
    assert numeric_verdict("6:45 AM", "What time did I wake up?", "7:00 AM") is None


def test_compound_duration_defers_to_the_judge():
    assert gold_numeric_range("4 years and 9 months") is None
    assert numeric_verdict(
        "4 years and 9 months", "How long had I worked there?", "9 years",
    ) is None


def test_gold_range_reads_the_benchmarks_own_tolerance():
    assert gold_numeric_range("7 days. 8 days (including the last day) is also acceptable.") == \
        {"dimension": "duration", "allowed": {7.0, 8.0}}
    assert gold_numeric_range("Four weeks") == {"dimension": "duration", "allowed": {28.0}}
    assert gold_numeric_range(
        "One week. Answers ranging from 7 days to 10 days are also acceptable."
    )["allowed"] == {7.0, 8.0, 9.0, 10.0}
    assert gold_numeric_range("27") == {"dimension": "count", "allowed": {27.0}}


def test_non_numeric_reference_defers_to_the_judge():
    assert gold_numeric_range("GPS system not functioning correctly") is None
    assert numeric_verdict("Fixing the fence", "What did I do?", "Fixing the fence.") is None


def test_duration_answers_are_compared_against_the_benchmark_range():
    gold = "One week. Answers ranging from 7 days to 10 days are also acceptable."
    question = "How long had I been using the new area rug?"
    assert numeric_verdict(gold, question, "7 days") is True
    assert numeric_verdict(gold, question, "9 days.") is True
    assert numeric_verdict(gold, question, "One month") is False
    assert numeric_verdict(gold, question, "Three weeks") is False


def test_bare_number_inherits_the_unit_the_question_asks_for():
    gold = "7 days. 8 days (including the last day) is also acceptable."
    question = "How many days before my friend's birthday party did I order her gift?"
    assert numeric_verdict(gold, question, "15") is False
    assert numeric_verdict(gold, question, "8") is True


def test_count_answers_reject_a_different_number():
    assert numeric_verdict("27", "How old was I when I moved?", "32") is False
    assert numeric_verdict("27", "How old was I when I moved?", "27") is True


def test_long_generation_is_not_treated_as_a_numeric_answer():
    gold = "7 days. 8 days (including the last day) is also acceptable."
    long_answer = " ".join(["Here is a detailed plan", "to clean your boots", "in 7 days", "or so"])
    assert numeric_verdict(gold, "How many days?", long_answer) is None


def test_evaluate_answer_uses_the_numeric_layer_without_calling_the_judge(monkeypatch):
    import evaluation.answer_semantic_eval as mod

    def _explode(*args, **kwargs):
        raise AssertionError("the judge must not be consulted for numeric answers")

    monkeypatch.setattr(mod.urllib.request, "urlopen", _explode)
    gold = "7 days. 8 days (including the last day) is also acceptable."

    verdict = evaluate_answer(
        "How many days before my friend's birthday party did I order her gift?",
        "15", [{"text": "I ordered the gift 7 days before the party."}],
        reference_answer=gold,
    )

    assert verdict["correct"] is False
    assert verdict["adjudication"] == "deterministic_numeric_range"
    assert verdict["judge_correct"] is None


def test_gate_verdicts_do_not_use_the_numeric_layer(monkeypatch):
    # The gate asks whether the evidence establishes the reference; applying the
    # numeric layer there would compare the reference against itself.
    import json

    import evaluation.answer_semantic_eval as mod

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return json.dumps({"response": json.dumps({
                "correct": True, "evidence_sufficient": True,
                "confidence": "high", "reason": "reference matches evidence.",
            })}).encode("utf-8")

    monkeypatch.setattr(mod.urllib.request, "urlopen", lambda *a, **k: _Response())
    gold = "7 days. 8 days (including the last day) is also acceptable."

    verdict = evaluate_answer(
        "How many days before my friend's birthday party did I order her gift?",
        gold, [{"text": "I ordered the gift 7 days before the party."}],
        candidate_is_reference=True, reference_answer=gold,
    )

    assert verdict["adjudication"] == "judge"


def test_lexical_skip_requires_more_than_a_threshold_overlap():
    # "Six weeks" against the reference "Four weeks" scores token-F1 0.5.
    assert not _lexical_skip_is_safe({"correct": True, "exact_match": 0.0, "token_f1": 0.5})
    assert _lexical_skip_is_safe({"correct": True, "exact_match": 0.0, "token_f1": 0.8})
    assert _lexical_skip_is_safe({"correct": True, "exact_match": 1.0, "token_f1": 0.4})
