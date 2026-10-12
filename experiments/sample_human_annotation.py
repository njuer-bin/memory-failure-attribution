"""Select a reproducible stratified sample for human attribution audit.

The source is the local deterministic-rescore JSONL produced by
``experiments.rescore_existing_results``. The sampled cases are exported as a
CSV so the researcher can annotate them without changing the experiment rows.

For LoCoMo, the exported Gold Evidence now includes the resolved benchmark
turn date/time when available. This is important for human annotation of
relative expressions such as ``yesterday``, ``last week`` and ``last Tuesday``:
the annotator should not have to infer the date from a turn ID alone.

Default allocation for the LoCoMo n=50 audit:
- F1_FORMATION: 12
- E0_EVIDENCE_INSUFFICIENCY: 4
- F4_RETRIEVAL: 2
- F5_CONTEXT: 1
- all remaining labels: 6

The mandatory strata are fixed first. The remaining slots are sampled from
non-mandatory labels first, so a dominant F1 class cannot silently consume all
of the exploratory slots. If there are not enough non-mandatory rows, the
remaining slots fall back to the full remaining pool.

Sampling is deterministic and stratified. The script never edits comparison
results and never calls a model.
"""
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
    "question_id",
    "question",
    "reference_answer",
    "gold_evidence",
    "gold_evidence_time_context",
    "auto_failure",
    "auto_real_correct",
    "human_evidence_sufficiency",
    "human_formation",
    "human_storage",
    "human_evolution",
    "human_retrieval",
    "human_rerank",
    "human_context",
    "human_answer_correct",
    "human_first_loss",
    "human_final_label",
    "agreement",
    "notes",
]


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _auto_failure(row: dict[str, Any]) -> str:
    failure = (row.get("modes", {}).get("real_memory") or {}).get("answer_failure_type")
    return str(failure or "NONE")


def _format_time_context(value: Any) -> str:
    if value is None or value == "":
        return ""
    return str(value)


def _evidence_time_index() -> dict[tuple[str, str], dict[str, Any]]:
    """Build a LoCoMo benchmark-turn index scoped by question/conversation.

    Turn IDs such as ``D1:turn_2`` are only unique *inside a LoCoMo
    conversation*. A global ``turn_id -> timestamp`` map can silently overwrite
    one conversation with another and give human annotators the wrong temporal
    anchor. The index therefore uses ``(question_id, turn_id)`` as its key.
    """
    try:
        from datasets.loader import iter_normalized

        index: dict[tuple[str, str], dict[str, Any]] = {}
        for record in iter_normalized("locomo_refined_public"):
            question_id = str(record.get("question_id") or "")
            for evidence in record.get("gold_evidence") or []:
                turn_id = str(evidence.get("turn_id") or "")
                if question_id and turn_id:
                    index[(question_id, turn_id)] = {
                        "timestamp": evidence.get("timestamp"),
                        "source_id": evidence.get("source_id"),
                    }
        return index
    except Exception:
        # Sampling must remain usable even when the optional benchmark files
        # are unavailable. In that case the time-context column stays blank.
        return {}


def _gold_evidence_text(
    row: dict[str, Any],
    *,
    time_index: dict[Any, dict[str, Any]] | None = None,
) -> tuple[str, str]:
    items = row.get("gold_evidence") or []
    rendered: list[str] = []
    contexts: list[str] = []
    time_index = time_index or {}
    question_id = str(row.get("question_id") or "")
    for item in items:
        if isinstance(item, dict):
            turn = item.get("source_turn_id") or item.get("turn_id") or "unknown_turn"
            text = item.get("text") or item.get("content") or ""
            # Prefer the timestamp already persisted with the Gold Evidence.
            # Only fall back to the benchmark index when the row itself does
            # not carry a timestamp. This prevents stale/ambiguous lookup data
            # from overriding the canonical evidence timestamp.
            timestamp = item.get("timestamp")
            if timestamp is None:
                resolved = time_index.get((question_id, str(turn)), {})
                timestamp = resolved.get("timestamp")
                # Backward-compatible support for unit tests/callers that pass
                # the old turn-only lookup shape.
                if timestamp is None:
                    timestamp = time_index.get(str(turn), {}).get("timestamp")
            time_text = _format_time_context(timestamp)
            if time_text:
                rendered.append(f"[{turn} | {time_text}] {text}")
                contexts.append(f"{turn} = {time_text}")
            else:
                rendered.append(f"[{turn}] {text}")
        else:
            rendered.append(str(item))
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
            raise ValueError(
                f"Not enough rows for {label}: need {count}, found {len(candidates)}"
            )
        for row in candidates[:count]:
            selected.append(row)
            selected_ids.add(str(row.get("question_id")))

    remaining_needed = total - len(selected)
    if remaining_needed < 0:
        raise ValueError("total must be at least the sum of mandatory strata")

    remaining = [r for r in rows if str(r.get("question_id")) not in selected_ids]
    exploratory = [r for r in remaining if _auto_failure(r) not in TARGET_COUNTS]
    rng.shuffle(exploratory)

    if len(exploratory) >= remaining_needed:
        selected.extend(exploratory[:remaining_needed])
    else:
        selected.extend(exploratory)
        exploratory_ids = {str(r.get("question_id")) for r in exploratory}
        fallback = [
            r for r in remaining if str(r.get("question_id")) not in exploratory_ids
        ]
        rng.shuffle(fallback)
        need = remaining_needed - len(exploratory)
        if len(fallback) < need:
            raise ValueError("Not enough rows to complete the requested sample")
        selected.extend(fallback[:need])

    rng.shuffle(selected)
    return selected


def build_rows(
    selected: list[dict[str, Any]],
    *,
    time_index: dict[Any, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
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
            "human_evidence_sufficiency": "",
            "human_formation": "",
            "human_storage": "",
            "human_evolution": "",
            "human_retrieval": "",
            "human_rerank": "",
            "human_context": "",
            "human_answer_correct": "",
            "human_first_loss": "",
            "human_final_label": "",
            "agreement": "",
            "notes": "",
        })
    return output


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
            raise ValueError(
                f"Not enough rows for {label}: need {count}, found {len(candidates)}"
            )
        for row in candidates[:count]:
            selected.append(row)
            selected_ids.add(str(row.get("question_id")))

    remaining_needed = total - len(selected)
    if remaining_needed < 0:
        raise ValueError("total must be at least the sum of mandatory strata")

    remaining = [r for r in rows if str(r.get("question_id")) not in selected_ids]
    exploratory = [r for r in remaining if _auto_failure(r) not in TARGET_COUNTS]
    rng.shuffle(exploratory)

    if len(exploratory) >= remaining_needed:
        selected.extend(exploratory[:remaining_needed])
    else:
        selected.extend(exploratory)
        exploratory_ids = {str(r.get("question_id")) for r in exploratory}
        fallback = [
            r for r in remaining if str(r.get("question_id")) not in exploratory_ids
        ]
        rng.shuffle(fallback)
        need = remaining_needed - len(exploratory)
        if len(fallback) < need:
            raise ValueError("Not enough rows to complete the requested sample")
        selected.extend(fallback[:need])

    rng.shuffle(selected)
    return selected


def sample(
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
    *,
    total: int = DEFAULT_TOTAL,
    seed: int = DEFAULT_SEED,
) -> Counter[str]:
    rows = _load_jsonl(input_path)
    if total < sum(TARGET_COUNTS.values()):
        raise ValueError("total must be at least the sum of mandatory strata")

    selected = _select_stratified(rows, total, seed)
    time_index = _evidence_time_index()
    output_rows = build_rows(selected, time_index=time_index)
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
