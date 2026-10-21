"""Tests for the controlled F3 evolution probe."""

from collections import Counter

from datasets.adapters import normalize_evolution_probe
from experiments.build_evolution_probe import build


def test_probe_covers_all_families_with_turn_level_gold():
    records = build()
    assert len(records) == 40
    families = Counter(r["metadata"]["evolution_family"] for r in records)
    assert families == {"update": 26, "stale": 6, "history": 8}


def test_adapter_marks_evolution_measured_and_builds_gold_turns():
    raw = build()[0]
    record = normalize_evolution_probe(raw, dataset="evolution_probe", index=0)
    assert record["metadata"]["measure_evolution"] is True
    assert record["metadata"]["requires_history"] is False
    evidence = record["gold_evidence"]
    assert len(evidence) == 1
    assert evidence[0]["turn_id"] == "s2:turn_1"
    assert evidence[0]["evidence_id"].endswith(":s2:turn_1")
    assert evidence[0]["text"] == "I currently live in Shanghai."


def test_history_scenarios_opt_into_history():
    history = [r for r in build() if r["metadata"]["evolution_family"] == "history"]
    record = normalize_evolution_probe(history[0], dataset="evolution_probe", index=0)
    assert record["metadata"]["requires_history"] is True
    assert record["gold_evidence"][0]["turn_id"] == "s1:turn_0"
