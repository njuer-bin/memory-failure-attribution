"""Tests for the comparable memory systems (no model calls)."""

from experiments import memory_systems as ms
from experiments import run_systems


def _record():
    return {
        "question": "Where does the user live?",
        "answer": "Shanghai",
        "gold_evidence": [{
            "evidence_id": "e0", "text": "I live in Shanghai.",
            "source_id": "s2", "turn_id": "s2:turn_0",
        }],
        "conversation": [
            {"session_id": "s1", "date": "2025-01-01",
             "messages": [{"role": "user", "content": "I live in Beijing."}]},
            {"session_id": "s2", "date": "2025-06-01",
             "messages": [{"role": "user", "content": "I live in Shanghai."}]},
        ],
    }


def test_verbatim_system_matches_turn_level_gold():
    system = ms.VerbatimSystem()
    system.ingest(_record())
    search = system.search("Where does the user live?")
    stages = ms.stage_dict(system.stages(_record()["gold_evidence"], search),
                           _record()["gold_evidence"], mode="verbatim")
    assert stages["formation"]["found"] == ["e0"]
    assert stages["storage"]["found"] == ["e0"]
    assert stages["evolution"]["details"]["measured"] is False
    assert len(search["context"]) == 2


def test_summary_system_uses_one_summary_per_session(monkeypatch):
    calls = []

    def fake_completion(prompt, model, **kwargs):
        calls.append(prompt)
        return "The user lives in Shanghai."

    monkeypatch.setattr(ms, "completion", fake_completion)
    system = ms.SummarySystem()
    system.ingest(_record())
    assert len(calls) == 2
    assert all(item["memory_type"] == "summary" for item in system.items)
    stages = system.stages(_record()["gold_evidence"], system.search("q"))
    assert len(stages["formation"]) == 2


def test_summary_falls_back_to_the_session_text(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("down")

    monkeypatch.setattr(ms, "completion", boom)
    system = ms.SummarySystem()
    system.ingest(_record())
    assert "Beijing" in system.items[0]["content"]


def test_summary_reports_fingerprint_fields():
    row = {
        "question_id": "q1",
        "gold_evidence": [{"evidence_id": "e0"}],
        "modes": {"verbatim": {
            "gold_evidence": [{"evidence_id": "e0"}],
            "formation": {"found": ["e0"], "details": {"measured": True}},
            "storage": {"found": ["e0"], "details": {"measured": True}},
            "evolution": {"found": [], "details": {"measured": False}},
            "retrieval": {"found": ["e0"], "details": {"measured": True}},
            "rerank": {"found": ["e0"], "details": {"measured": True}},
            "context": {"found": ["e0"], "details": {"measured": True}},
            "answer": {"semantic_correct": True},
            "evidence_sufficiency": {"status": "sufficient"},
            "answer_failure_type": None,
        }},
    }
    result = run_systems._summary([row], ("verbatim",))
    system = result["systems"]["verbatim"]
    assert system["semantic_accuracy"] == 1.0
    assert system["answer_failure_distribution"] == {"none": 1}
    assert system["gate_distribution"] == {"sufficient": 1}
    assert system["stage_recall"].get("evolution") is None
    assert "evolution" in system["unmeasured_stages"]
