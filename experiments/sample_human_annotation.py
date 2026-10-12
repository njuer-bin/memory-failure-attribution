"""Select a reproducible stratified sample for human attribution audit."""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results" / "oracle_experiments" / "comparison_rescored.jsonl"
DEFAULT_OUTPUT = ROOT / "results" / "human_annotation" / "annotation_template.csv"
DEFAULT_SEED = 20261012
DEFAULT_TOTAL = 25
TARGET_COUNTS = {
    "F1_FORMATION": 12,
    "E0_EVIDENCE_INSUFFICIENCY": 4,
    "F4_RETRIEVAL": 2,
    "F5_CONTEXT": 1,
}
FIELDS = [
    "question_id", "question", "reference_answer", "gold_evidence",
    "gold_evidence_time_context", "auto_failure", "auto_real_correct",
    "human_evidence_sufficiency", "human_formation", "human_storage",
    "human_evolution", "human_retrieval", "human_rerank", "human_context",
    "human_answer_correct", "human_first_loss", "human_final_label",
    "agreement", "notes",
]


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _auto_failure(row: dict[str, Any]) -> str:
    failure = (row.get("modes", {}).get("real_memory") or {}).get("answer_failure_type")
    return str(failure or "NONE")


def _format_time_context(value: Any) -> str:
    return "" if value is None or value == "" else str(value)


def _evidence_time_index() -> dict[tuple[str, str], dict[str, Any]]:
    """Return benchmark timestamps keyed by (question_id, turn_id).

    LoCoMo turn IDs such as D1:turn_2 repeat across conversations, so a global
    turn-id map can overwrite one conversation's timestamp with another's.
    """
    try:
        from datasets.loader import iter_normalized

        index: dict[tuple[str, str], dict[str, Any]] = {}
        for record in iter_normalized("locomo_refined_public"):
            qid = str(record.get("question_id") or "")
            for evidence in record.get("gold_evidence") or []:
                turn_id = str(evidence.get("turn_id") or "")
                if qid and turn_id:
                    index[(qid, turn_id)] = {
                        "timestamp": evidence.get("timestamp"),
                        "source_id": evidence.get("source_id"),
                    }
        return index
    except Exception:
        return {}


def _gold_evidence_text(
    row: dict[str, Any],
    *,
    time_index: dict[Any, dict[str, Any]] | None = None,
) -> tuple[str, str]:
    rendered: list[str] = []
    contexts: list[str] = []
    time_index = time_index or {}
    qid = str(row.get("question_id") or "")
    for item in row.get("gold_evidence") or []:
        if not isinstance(item, dict):
            rendered.append(str(item))
            continue
        turn = item.get("source_turn_id") or item.get("turn_id") or "unknown_turn"
        text = item.get("text") or item.get("content") or ""
        # Persisted Gold Evidence is authoritative. The benchmark index is only
        # a fallback for legacy rows that lack timestamp metadata.
        timestamp = item.get("timestamp")
        if timestamp is None:
            timestamp = time_index.get((qid, str(turn)), {}).get("timestamp")
            # Backward-compatible test/caller support.
            if timestamp is None:
                timestamp = time_index.get(str(turn), {}).get("timestamp")
        time_text = _format_time_context(timestamp)
        if time_text:
            rendered.append(f"[{turn} | {time_text}] {text}")
            contexts.append(f"{turn} = {time_text}")
        else:
            rendered.append(f"[{turn}] {text}")
    return "\n".join(rendered), "; ".join(contexts)


def _select_stratified(rows: list[dict[str, Any]], total: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        buckets.setdefault(_auto_failure(row), []).append(row)

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    for label, count in TARGET_COUNTS.items():
        candidates = list(buckets.get(label, []))
        rng.shuffle(candidates)
        if len(candidates) < count:
            raise ValueError(f"Not enough rows for {label}: need {count}, found {len(candidates)}")
        for row in candidates[:count]:
            selected.append(row)
            selected_ids.add(str(row.get("question_id")))

    remaining_needed = total - len(selected)
    if remaining_needed < 0:
        raise ValueError("total must be at least the sum of mandatory strata")
    remaining = [r for r in rows if str(r.get("question_id")) not in selected_ids]
    exploratory = [r for r in remaining if _auto_failure(r) not in TARGET_COUNTS]
    rng.shuffle(exploratory)
    selected.extend(exploratory[:remaining_needed])
    if len(selected) < total:
        exploratory_ids = {str(r.get("question_id")) for r in exploratory}
        fallback = [r for r in remaining if str(r.get("question_id")) not in exploratory_ids]
        rng.shuffle(fallback)
        selected.extend(fallback[: total - len(selected)])
    if len(selected) != total:
        raise ValueError("Not enough rows to complete the requested sample")
    rng.shuffle(selected)
    return selected


def build_rows(
    selected: list[dict[str, Any]],
    *,
    time_index: dict[Any, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    output = []
    for row in selected:
        real = row.get("modes", {}).get("real_memory") or {}
        answer = real.get("answer") or {}
        evidence_text, time_context = _gold_evidence_text(row, time_index=time_index)
        output.append({
            "question_id": row.get("question_id", ""),
            "question": row.get("question", ""),
            "reference_answer": row.get("gold_answer", ""),
            "gold_evidence": evidence_text,
            "gold_evidence_time_context": time_context,
            "auto_failure": _auto_failure(row),
            "auto_real_correct": answer.get("correct", ""),
            "human_evidence_sufficiency": "", "human_formation": "",
            "human_storage": "", "human_evolution": "", "human_retrieval": "",
            "human_rerank": "", "human_context": "", "human_answer_correct": "",
            "human_first_loss": "", "human_final_label": "", "agreement": "", "notes": "",
        })
    return output


def sample(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT, *, total: int = DEFAULT_TOTAL, seed: int = DEFAULT_SEED) -> Counter[str]:
    rows = _load_jsonl(input_path)
    if total < sum(TARGET_COUNTS.values()):
        raise ValueError("total must be at least the sum of mandatory strata")
    selected = _select_stratified(rows, total, seed)
    output_rows = build_rows(selected, time_index=_evidence_time_index())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)
    counts = Counter(row["auto_failure"] for row in output_rows)
    print(f"Selected {len(output_rows)} cases (seed={seed})")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")
    print(f"Time-context entries: {sum(bool(r['gold_evidence_time_context']) for r in output_rows)}/{len(output_rows)}")
    print(f"Output: {output_path}")
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Sample cases for human attribution audit")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--total", type=int, default=DEFAULT_TOTAL)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    sample(Path(args.input), Path(args.output), total=args.total, seed=args.seed)


if __name__ == "__main__":
    main()
