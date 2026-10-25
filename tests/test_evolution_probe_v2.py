"""Tests for the F3 evolution probe v2 (distractor sessions)."""

import json
from collections import Counter
from pathlib import Path

from datasets.adapters import normalize_evolution_probe
from datasets.loader import iter_normalized
from experiments.build_evolution_probe_v2 import (
    DISTRACTOR_DATES,
    N_DISTRACTORS,
    ROOT,
    _distractor_sessions,
    _DISTRACTOR_TURNS,
)


def _v2_path() -> Path:
    return ROOT / "datasets" / "evolution_probe" / "probe_v2.jsonl"


def test_v2_keeps_v1_questions_and_gold():
    v1 = {
        json.loads(line)["question_id"]: json.loads(line)
        for line in (_v2_path().parent / "probe.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    }
    v2 = [json.loads(line) for line in _v2_path().read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(v2) == 40
    for rec in v2:
        base = v1[rec["question_id"]]
        assert rec["question"] == base["question"]
        assert rec["answer"] == base["answer"]
        assert rec["gold_turns"] == base["gold_turns"]
        assert rec["metadata"]["evolution_family"] == base["metadata"]["evolution_family"]
        assert rec["metadata"]["probe_version"] == 2


def test_v2_adds_exactly_eight_distractors():
    v2 = [json.loads(line) for line in _v2_path().read_text(encoding="utf-8").splitlines() if line.strip()]
    for rec in v2:
        assert len(rec["sessions"]) == 2 + N_DISTRACTORS
        assert rec["metadata"]["n_distractor_sessions"] == N_DISTRACTORS
        d_ids = [s["session_id"] for s in rec["sessions"] if s["session_id"].startswith("d")]
        assert d_ids == [f"d{i}" for i in range(1, N_DISTRACTORS + 1)]


def test_distractor_dates_never_collide_with_real_session_dates():
    # Distractor dates must differ from the v1 real dates so provenance stays clean
    real_dates = {"2025-01-15", "2025-06-20", "2025-09-10"}
    assert not real_dates & set(DISTRACTOR_DATES)


def test_distractor_banks_are_valid():
    for bank in _DISTRACTOR_TURNS:
        assert 1 <= len(bank) <= 2
        for turn in bank:
            assert 40 < len(turn) < 300


def test_distractor_sessions_sampled_without_replacement():
    from experiments.build_evolution_probe_v2 import _distractor_sessions
    import random
    rng = random.Random(0)
    for _ in range(10):
        sessions = _distractor_sessions(rng)
        assert len({s["session_id"] for s in sessions}) == N_DISTRACTORS


def test_loader_normalizes_v2_dataset():
    records = list(iter_normalized("evolution_probe_v2"))
    assert len(records) == 40
    rec = records[0]
    assert rec["dataset"] == "evolution_probe_v2"
    assert len(rec["conversation"]) == 2 + N_DISTRACTORS
    assert rec["metadata"]["measure_evolution"] is True
    # gold evidence still points at the v1 turn
    assert rec["gold_evidence"][0]["evidence_id"].endswith(":s2:turn_1")


def test_v2_records_normalize_through_v1_adapter():
    raw = json.loads(_v2_path().read_text(encoding="utf-8").splitlines()[0])
    record = normalize_evolution_probe(raw, dataset="evolution_probe_v2", index=0)
    assert record["metadata"]["normalization"] == "evolution_probe_v2"
    assert record["metadata"]["probe_version"] == 2
    distractor_ids = {s["session_id"] for s in record["conversation"]
                      if s["session_id"].startswith("d")}
    assert len(distractor_ids) == N_DISTRACTORS
    # distractor turns never appear as gold evidence
    gold_texts = {e["text"] for e in record["gold_evidence"]}
    distractor_texts = {m["content"] for s in record["conversation"]
                        if s["session_id"].startswith("d") for m in s["messages"]}
    assert not gold_texts & distractor_texts
