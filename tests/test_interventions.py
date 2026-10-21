from types import SimpleNamespace

from evaluation import answer_generation
from experiments import interventions
from memory_engine.evidence import EvidenceBuilder


def _row(failure="F1_FORMATION", correct=False, stages=None):
    stages = stages or {}
    mode = {
        "answer_failure_type": failure,
        "answer": {"semantic_correct": correct},
    }
    for stage in interventions.MEASURED_STAGES:
        mode[stage] = {"found": list(stages.get(stage, []))}
    return {
        "question_id": "q",
        "gold_evidence": [{"evidence_id": "e0"}],
        "modes": {"real_memory": mode},
    }


def test_first_loss_target_maps_only_attributable_failures():
    assert interventions.first_loss_target(_row()["modes"]["real_memory"]) == "formation"
    assert interventions.first_loss_target(
        _row("F4_RETRIEVAL")["modes"]["real_memory"]) == "retrieval"
    assert interventions.first_loss_target(
        _row("F5_CONTEXT")["modes"]["real_memory"]) == "context"
    assert interventions.first_loss_target(
        _row("F6_REASONING_CANDIDATE")["modes"]["real_memory"]) == "reasoning"
    assert interventions.first_loss_target(
        _row("E0_EVIDENCE_INSUFFICIENT")["modes"]["real_memory"]) is None


def test_path_target_is_reasoning_when_evidence_reaches_context():
    # Only formation is missing; the answer context still carries the evidence,
    # so a formation repair cannot change the answer.
    row = _row(stages={"formation": [], "storage": ["e0"], "retrieval": ["e0"],
                       "rerank": ["e0"], "context": ["e0"]})
    assert interventions.arm_target(row, "path") == "reasoning"
    assert interventions.arm_target(row, "first_loss") == "formation"


def test_path_target_widens_context_when_context_is_the_deepest_drop():
    row = _row(stages={"formation": [], "storage": [], "retrieval": ["e0"],
                       "rerank": ["e0"], "context": []})
    assert interventions.arm_target(row, "path") == "context"


def test_path_target_widens_retrieval_when_rerank_also_drops():
    row = _row(stages={"formation": [], "storage": [], "retrieval": ["e0"],
                       "rerank": [], "context": []})
    assert interventions.arm_target(row, "path") == "retrieval"


def test_correct_and_unattributable_rows_are_not_targets():
    correct = _row(correct=True)
    assert interventions.arm_target(correct, "agnostic") is None
    e0 = _row(failure="E0_EVIDENCE_INSUFFICIENT")
    assert interventions.arm_target(e0, "first_loss") is None
    assert interventions.arm_target(e0, "agnostic") is None


def test_agnostic_arm_targets_every_attributable_failure():
    assert interventions.arm_target(_row("F6_REASONING_CANDIDATE"), "agnostic") == "all"


class _FakeStore:
    def __init__(self, raw, facts=()):
        self._raw = raw
        self._facts = list(facts)
        self.inserted = []

    def all_raw(self, user_id):
        return self._raw

    def active_facts(self, user_id, include_history=False):
        return self._facts

    def events(self, user_id, start_time=None, end_time=None):
        return []

    def relations(self, user_id):
        return []

    def rules(self, user_id):
        return []

    def profiles(self, user_id):
        return []

    def insert_event(self, event):
        self.inserted.append(event)

    def embed(self, memory_id, user_id, vector):
        pass


class _FakeEngine:
    def __init__(self, store):
        self.store = store
        self.embedder = SimpleNamespace(embed=lambda text: [0.0])
        self.vector_index = SimpleNamespace(add=lambda *args: None)


def test_write_through_only_adds_unrepresented_turns_with_provenance():
    raw = [
        {"id": "r0", "content": "I live in Berlin.", "timestamp": 1,
         "session_id": "s", "source_turn_id": "s:turn_0"},
        {"id": "r1", "content": "My sister painted a mural.", "timestamp": 2,
         "session_id": "s", "source_turn_id": "s:turn_1"},
    ]
    facts = [{"content": "I live in Berlin.", "source_turn_id": "s:turn_0"}]
    engine = _FakeEngine(_FakeStore(raw, facts))
    written = interventions.write_through_verbatim(engine, "u")
    assert written == 1
    assert len(engine.store.inserted) == 1
    event = engine.store.inserted[0]
    assert event.content == "My sister painted a mural."
    assert event.source_turn_id == "s:turn_1"
    assert event.source_raw_id == "r1"


def test_evidence_builder_type_cap_changes_context_size():
    candidates = [
        {"content": f"raw {i}", "memory_type": "raw"} for i in range(6)
    ]
    assert len(EvidenceBuilder().build(candidates, top_k=10)) == 3
    assert len(EvidenceBuilder().build(candidates, top_k=10, type_cap=6)) == 6


def test_self_checked_answer_makes_two_temperature_zero_calls(monkeypatch):
    calls = []

    def fake_completion(prompt, model, **kwargs):
        calls.append(prompt)
        return "draft" if len(calls) == 1 else "final"

    monkeypatch.setattr("evaluation.llm_api.completion", fake_completion)
    answer = answer_generation.generate_self_checked_answer(
        "Where does the user live?",
        [{"content": "I live in Berlin."}],
    )
    assert answer == "final"
    assert len(calls) == 2
    assert "Draft answer: draft" in calls[1]


def test_run_record_orchestrates_arms_and_targets(monkeypatch):
    from experiments import run_interventions as runner
    from memory_engine.models import SearchRequest

    class FakeEngine:
        def __init__(self):
            self.store = _FakeStore([
                {"id": "r0", "content": "I live in Berlin.", "timestamp": 1,
                 "session_id": "s", "source_turn_id": "s:turn_0"},
            ])
            self.embedder = SimpleNamespace(embed=lambda text: [0.0])
            self.vector_index = SimpleNamespace(add=lambda *args: None)
            self.last_search_trace = {"context": [{"content": "I live in Berlin."}]}

        def search(self, request: SearchRequest):
            return [{"content": "I live in Berlin.", "memory_type": "raw"}]

    monkeypatch.setattr(runner.runner, "_real_engine", lambda record, idx: (FakeEngine(), "u"))
    monkeypatch.setattr(runner, "generate_answer", lambda question, context: "Berlin")
    monkeypatch.setattr(runner, "generate_self_checked_answer", lambda question, context: "Berlin")

    def fake_semantic(question, answer, gold, reference):
        answer = dict(answer)
        answer["semantic_correct"] = False
        answer["semantic_confidence"] = "high"
        return answer

    monkeypatch.setattr(runner.runner, "_semantic_eval", fake_semantic)

    baseline_row = _row(stages={
        "formation": [], "storage": ["e0"], "retrieval": ["e0"],
        "rerank": ["e0"], "context": ["e0"],
    })
    baseline_row["modes"]["real_memory"]["evidence_sufficiency"] = {"status": "sufficient"}
    record = {"question": "Where does the user live?", "answer": "Berlin"}
    rows = runner.run_record(record, 0, baseline_row, ("first_loss", "path", "agnostic"))
    by_arm = {row["arm"]: row for row in rows}
    assert by_arm["first_loss"]["target_stage"] == "formation"
    assert by_arm["path"]["target_stage"] == "reasoning"
    assert by_arm["agnostic"]["target_stage"] == "all"
    assert all(row["repaired"] is not None for row in rows)
