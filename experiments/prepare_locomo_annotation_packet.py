#!/usr/bin/env python3
"""Prepare a local LoCoMo annotation packet from the official dataset.

The generated packet contains raw dialogue excerpts and should remain local.
Do not commit the generated output to this repository.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def index_turns(conversation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for key, value in conversation.items():
        if not key.startswith("session_") or not isinstance(value, list):
            continue
        for turn in value:
            dia_id = turn.get("dia_id")
            if dia_id:
                indexed[dia_id] = turn
    return indexed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, type=Path,
                        help="Path to the official locomo10.json file")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("docs/LOCOMO_PILOT_MANIFEST.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.home() / "locomo_pilot_annotation_packet.jsonl",
        help="Local output path; defaults outside the repository",
    )
    args = parser.parse_args()

    dataset = load_json(args.dataset)
    manifest = load_json(args.manifest)
    by_id = {sample.get("sample_id"): sample for sample in dataset}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with args.output.open("w", encoding="utf-8") as handle:
        for item in manifest["questions"]:
            sample_id = item["conversation_id"]
            if sample_id not in by_id:
                raise ValueError(f"Conversation not found: {sample_id}")

            sample = by_id[sample_id]
            qa_index = item["qa_index"]
            qa_items = sample.get("qa", [])
            if qa_index >= len(qa_items):
                raise IndexError(f"{sample_id} qa_index={qa_index} out of range")

            qa = qa_items[qa_index]
            if qa.get("category") != 1:
                raise ValueError(
                    f"{item['question_id']} is not category 1 multi-hop"
                )
            if qa.get("question") != item["question"]:
                raise ValueError(f"Question mismatch for {item['question_id']}")
            if str(qa.get("answer")) != str(item["reference_answer"]):
                raise ValueError(f"Reference answer mismatch for {item['question_id']}")

            official_evidence = qa.get("evidence", [])
            expected_evidence = item["evidence_turn_ids"]
            if set(official_evidence) != set(expected_evidence):
                raise ValueError(
                    f"Evidence ID mismatch for {item['question_id']}: "
                    f"official={official_evidence}, manifest={expected_evidence}"
                )

            turns = index_turns(sample["conversation"])
            evidence_turns = []
            for dia_id in expected_evidence:
                if dia_id not in turns:
                    raise KeyError(f"Turn {dia_id} not found in {sample_id}")
                turn = turns[dia_id]
                evidence_turns.append({
                    "source_dia_id": dia_id,
                    "speaker": turn.get("speaker"),
                    "text": turn.get("text"),
                    "timestamp": turn.get("timestamp"),
                })

            record = {
                "question_id": item["question_id"],
                "conversation_id": sample_id,
                "qa_index": qa_index,
                "question": item["question"],
                "reference_answer": item["reference_answer"],
                "category_id": 1,
                "category_name": "multi_hop",
                "evidence_turns": evidence_turns,
                "audit_flag": item.get("audit_flag", ""),
                "dataset_attribution": (
                    "Maharana et al., Evaluating Very Long-Term Conversational "
                    "Memory of LLM Agents; snap-research/locomo, CC BY-NC 4.0"
                ),
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1

    print(f"Wrote {written} records to: {args.output}")
    print("The output contains CC BY-NC 4.0 dialogue excerpts.")
    print("Keep it local; do not commit the generated packet to Git.")


if __name__ == "__main__":
    main()
