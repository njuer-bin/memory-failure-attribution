"""Export multi-hop candidates into a human-review CSV template."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results" / "multihop_candidates" / "locomo_refined_public_candidates.jsonl"
DEFAULT_OUTPUT = ROOT / "results" / "multihop_candidates" / "locomo_refined_public_human_review.csv"

FIELDS = [
    "question_id", "question", "reference_answer", "gold_evidence",
    "candidate_reasons", "human_is_multi_hop", "human_hop_count",
    "human_hop_type", "human_ordered_path", "human_relations",
    "human_bridge_evidence", "annotation_status", "notes",
]


def _join_evidence(items: list[dict]) -> str:
    rows = []
    for item in items:
        evidence_id = item.get("evidence_id", item.get("id", ""))
        text = str(item.get("text", item.get("content", "")) or "").replace("\n", " ").strip()
        rows.append(f"{evidence_id}: {text}")
    return " || ".join(rows)


def export(input_path: Path, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with input_path.open("r", encoding="utf-8") as src, output_path.open("w", encoding="utf-8-sig", newline="") as dst:
        writer = csv.DictWriter(dst, fieldnames=FIELDS)
        writer.writeheader()
        for line in src:
            if not line.strip():
                continue
            item = json.loads(line)
            review = item.get("review") or {}
            writer.writerow({
                "question_id": item.get("question_id", ""),
                "question": item.get("question", ""),
                "reference_answer": item.get("reference_answer", ""),
                "gold_evidence": _join_evidence(item.get("gold_evidence") or []),
                "candidate_reasons": ";".join(item.get("candidate_reasons") or []),
                "human_is_multi_hop": "",
                "human_hop_count": "",
                "human_hop_type": "",
                "human_ordered_path": "",
                "human_relations": "",
                "human_bridge_evidence": "",
                "annotation_status": review.get("status", "unreviewed"),
                "notes": "",
            })
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    count = export(Path(args.input), Path(args.output))
    print(f"Exported {count} review rows -> {args.output}")


if __name__ == "__main__":
    main()
