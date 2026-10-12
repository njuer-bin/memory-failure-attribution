from __future__ import annotations

import csv
import json
from pathlib import Path

from experiments.export_multihop_review_csv import FIELDS, export


def test_export_creates_reviewable_csv(tmp_path: Path):
    source = tmp_path / "candidates.jsonl"
    output = tmp_path / "review.csv"
    source.write_text(json.dumps({
        "question_id": "q1",
        "question": "Why did Alice leave?",
        "reference_answer": "Because...",
        "gold_evidence": [
            {"evidence_id": "e1", "text": "Alice joined."},
            {"evidence_id": "e2", "text": "Alice left."},
        ],
        "candidate_reasons": ["multiple_gold_evidence_items"],
        "review": {"status": "unreviewed"},
    }, ensure_ascii=False) + "\n", encoding="utf-8")

    assert export(source, output) == 1
    with output.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    assert rows[0]["question_id"] == "q1"
    assert "e1: Alice joined." in rows[0]["gold_evidence"]
    assert rows[0]["human_is_multi_hop"] == ""
    assert rows[0]["human_hop_count"] == ""
    assert rows[0]["annotation_status"] == "unreviewed"
    assert list(rows[0].keys()) == FIELDS
