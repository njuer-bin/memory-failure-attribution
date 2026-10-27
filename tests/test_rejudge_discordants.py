"""Tests for the discordant re-judge pass (no model calls)."""

from experiments import rejudge_discordants as rejudge


def _pair(qid="q1", arm="agnostic", base=False, repaired=True):
    return {
        "question_id": qid,
        "arm": arm,
        "skipped": False,
        "target_stage": "all",
        "baseline": {"semantic_correct": base, "answer": "old"},
        "repaired": {"semantic_correct": repaired, "answer": "new"},
    }


def _baseline_row(qid="q1"):
    return {
        "question_id": qid,
        "question": "q?",
        "gold_answer": "a",
        "gold_evidence": [{"evidence_id": "e0", "text": "a"}],
    }


def test_changed_verdict_is_reported(monkeypatch):
    verdicts = iter([
        {"correct": True, "adjudication": "judge"},
        {"correct": True, "adjudication": "judge"},
    ])
    monkeypatch.setattr(rejudge, "evaluate_answer", lambda *a, **k: next(verdicts))
    result = rejudge.rejudge_pair(_pair(), _baseline_row())
    assert result["old"] == (False, True)
    assert result["new"] == (True, True)
    assert result["changed"] is True


def test_summary_recomputes_net_flips(monkeypatch):
    monkeypatch.setattr(
        rejudge, "evaluate_answer",
        lambda *a, **k: {"correct": True, "adjudication": "judge"},
    )
    rows = [_pair("q1", base=False, repaired=True), _pair("q2", base=True, repaired=False)]
    baseline = [_baseline_row("q1"), _baseline_row("q2")]
    import json, tempfile, os
    with tempfile.TemporaryDirectory() as tmp:
        ip = os.path.join(tmp, "i.jsonl")
        bp = os.path.join(tmp, "b.jsonl")
        with open(ip, "w", encoding="utf-8") as fh:
            fh.write("".join(json.dumps(r) + "\n" for r in rows))
        with open(bp, "w", encoding="utf-8") as fh:
            fh.write("".join(json.dumps(r) + "\n" for r in baseline))
        result = rejudge.run(rejudge.Path(ip), rejudge.Path(bp), ("agnostic",))
    arm = result["arms"]["agnostic"]
    assert result["discordant_pairs"] == 2
    assert arm["pairs_changed"] == 2
    # q1 old gain is removed (True/True); q2 old loss becomes a tie (True/True).
    assert arm["new_net_flips"] == 0


def test_non_discordant_pairs_are_skipped(monkeypatch):
    monkeypatch.setattr(rejudge, "evaluate_answer", lambda *a, **k: {"correct": True})
    rows = [_pair("q1", base=True, repaired=True)]
    import json, tempfile, os
    with tempfile.TemporaryDirectory() as tmp:
        ip = os.path.join(tmp, "i.jsonl")
        bp = os.path.join(tmp, "b.jsonl")
        with open(ip, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(rows[0]) + "\n")
        with open(bp, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(_baseline_row()) + "\n")
        result = rejudge.run(rejudge.Path(ip), rejudge.Path(bp), ("agnostic",))
    assert result["discordant_pairs"] == 0
