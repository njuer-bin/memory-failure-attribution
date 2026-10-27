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


def test_semantic_system_runs_inside_the_same_runner():
    system = ms.SemanticSystem()
    system.ingest(_record())
    search = system.search("Where does the user live?")
    stages = ms.stage_dict(
        system.stages(_record()["gold_evidence"], search),
        _record()["gold_evidence"], mode="semantic",
    )
    assert stages["formation"]["found"] == ["e0"]
    assert stages["evolution"]["details"]["measured"] is False
    assert search["context"]


def test_context_budget_is_applied_uniformly():
    items = [{"content": "x" * 100}, {"content": "y" * 100}, {"content": "z" * 100}]
    assert len(run_systems._cap_context(items, 250)) == 2
    assert len(run_systems._cap_context(items, 1000)) == 3
    assert run_systems._cap_context([], 100) == []


def test_embedding_search_honours_candidate_and_top_k():
    import types

    class Stub(ms._EmbeddingSystem):
        def __init__(self):
            self.embedder = types.SimpleNamespace(embed=lambda text: [1.0, 0.0])
            self.items = [
                {"id": f"i{i}", "content": str(i), "vector": [1.0, float(i) / 10]}
                for i in range(8)
            ]

    result = Stub().search("q", candidate_k=3, top_k=2)
    assert len(result["retrieval"]) == 3
    assert len(result["rerank"]) == 2
    assert len(result["context"]) == 2
    assert len(Stub().search("q", candidate_k=50, top_k=50)["retrieval"]) == 8


def test_run_records_search_knobs_in_summary(tmp_path, monkeypatch):
    import json

    monkeypatch.setattr(run_systems, "iter_normalized",
                        lambda dataset, limit=None: iter([_record()][:1]))
    monkeypatch.setattr(run_systems.runner, "_evidence_sufficiency",
                        lambda *a, **k: {"status": "sufficient"})
    monkeypatch.setattr(run_systems.runner, "_score_mode_answer",
                        lambda *a, **k: {"answer": "Shanghai", "correct": True})
    monkeypatch.setattr(run_systems.runner, "_semantic_eval",
                        lambda *a, **k: {"answer": "Shanghai", "correct": True,
                                         "semantic_correct": True,
                                         "semantic_confidence": "high"})
    out = tmp_path / "run"
    run_systems.run("dummy", ("verbatim",), 1, out, False,
                    context_chars=6000, candidate_k=5, top_k=3)
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["search"] == {"candidate_k": 5, "top_k": 3, "context_chars": 6000}


def test_ablation_variants_registered():
    for name in ("semantic_rawwrite", "summary_raw", "verbatim_hybrid"):
        assert name in ms.SYSTEMS


def test_summary_raw_ingest_does_not_call_llm(monkeypatch):
    calls = []
    monkeypatch.setattr(ms, "completion", lambda *a, **k: calls.append(1) or "summary")
    system = ms.SummaryRawSystem()
    system.ingest(_record())
    assert calls == []
    assert system.items
    assert any("I live in Shanghai." in item["content"] for item in system.items)


def test_hybrid_verbatim_search_ranks_lexical_match_first(monkeypatch):
    system = ms.HybridVerbatimSystem()
    monkeypatch.setattr(system.embedder, "embed", lambda text: [1.0, 0.0])
    system.items = [
        {"id": "a", "content": "completely unrelated", "vector": [0.0, 1.0]},
        {"id": "b", "content": "Shanghai apartment lease", "vector": [0.0, 1.0]},
    ]
    result = system.search("Where is the Shanghai apartment?", candidate_k=2, top_k=2)
    assert result["retrieval"][0]["id"] == "b"
    assert len(result["context"]) == 2
